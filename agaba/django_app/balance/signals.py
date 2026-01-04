import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from account.utils import save_pdf_to_db
from order.models import Order

from account.models import CustomUser

from .models import (Replenishment, Withdrawal,
                     OrderOperation,
                     AllOperation, Balance)
from .kafka_events import publish_operation_event

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Replenishment)
def create_or_update_all_operation_for_replenishment(
    sender, instance, created, **kwargs
):
    """
    Создает или обновляет запись в AllOperation при создании/изменении пополнения.
    Также генерирует PDF и сохраняет его в базу данных.
    """
    try:
        with transaction.atomic():
            all_operation, created_op = AllOperation.objects.get_or_create(
                operation_id=instance.operation_id,
                defaults={
                    'user': instance.user,
                    'amount': instance.amount_replenishment,
                    'type_operation': 'replenishment',
                    'status_operation': instance.status_operation,
                    'payment_type': instance.payment_type,
                    'details': {
                        'operation_id': str(instance.operation_id),
                        'type': 'Пополнение',
                        'company': {
                            'id': instance.company.id,
                            'name': instance.company.name,
                            'inn': instance.company.inn,
                            'kpp': instance.company.kpp,
                            'legal_address': instance.company.legal_address,
                            'ogrn': instance.company.ogrn,
                            'is_hidden': instance.company.is_hidden,
                        },
                        'user': {
                            'id': instance.user.id,
                            'username': instance.user.username,
                            'email': instance.user.email,
                        }
                    }
                }
            )

            if not created_op:
                updated_fields = []
                if all_operation.status_operation != instance.status_operation:
                    all_operation.status_operation = instance.status_operation
                    updated_fields.append('status_operation')
                if all_operation.payment_type != instance.payment_type:
                    all_operation.payment_type = instance.payment_type
                    updated_fields.append('payment_type')

                company_data = all_operation.details.get('company', {})
                if any(
                    company_data.get(field) != getattr(instance.company, field)
                    for field in ['id', 'name', 'inn', 'kpp', 'legal_address', 'ogrn']
                ):
                    all_operation.details['company'] = {
                        'id': instance.company.id,
                        'name': instance.company.name,
                        'inn': instance.company.inn,
                        'kpp': instance.company.kpp,
                        'legal_address': instance.company.legal_address,
                        'ogrn': instance.company.ogrn,
                        'is_hidden': instance.company.is_hidden,
                    }
                    updated_fields.append('details')

                user_data = all_operation.details.get('user', {})
                if any(
                    user_data.get(field) != getattr(instance.user, field)
                    for field in ['id', 'username', 'email']
                ):
                    all_operation.details['user'] = {
                        'id': instance.user.id,
                        'username': instance.user.username,
                        'email': instance.user.email,
                    }
                    updated_fields.append('details')

                if updated_fields:
                    all_operation.save(update_fields=updated_fields)
                    logger.info(f"Обновлены поля {', '.join(updated_fields)} для операции {instance.operation_id}.")

            # Генерация и сохранение PDF
            if created:
                try:
                    save_pdf_to_db(instance)
                    logger.info(f"PDF успешно сгенерирован и сохранен для операции {instance.operation_id}.")
                except Exception as e:
                    logger.error(f"Ошибка при генерации PDF: {e}")

    except Exception as e:
        logger.error(f"Ошибка при обработке операции пополнения: {e}")
        raise


@receiver(post_save, sender=Withdrawal)
def create_or_update_all_operation_for_withdrawal(
    sender, instance, created, **kwargs
):
    """
    Создает или обновляет запись в AllOperation при создании/изменении вывода.
    """
    try:
        with transaction.atomic():
            all_operation, created_op = AllOperation.objects.get_or_create(
                operation_id=instance.withdrawal_operation_id,
                defaults={
                    'user': instance.user,
                    'amount': instance.amount_withdrawal,
                    'type_operation': 'withdrawal',
                    'status_operation': instance.status_operation,
                    'details': {
                        'operation_id': str(instance.withdrawal_operation_id),
                        'type': 'Вывод',
                        'number_account': instance.number_account,
                        'inn': instance.inn,
                        'bik': instance.bik,
                        'ks': instance.ks,
                    }
                }
            )

            if not created_op and all_operation.status_operation != instance.status_operation:
                all_operation.status_operation = instance.status_operation
                all_operation.save()
                logger.info(
                    f"Статус операции {instance.withdrawal_operation_id} обновлен в AllOperation."
                )

    except Exception as e:
        logger.error(f"Ошибка при создании/обновлении записи в AllOperation: {e}")
        raise


@receiver(post_save, sender=Order)
def create_order_related_operations(sender, instance, created, **kwargs):
    """
    Создает записи в OrderOperation и AllOperation при создании заказа (Order).
    Также обновляет статус товара in_stock на False.
    """
    if created:
        try:
            with transaction.atomic():
                type_operation_mapping = {
                    'is_cash': 'account',
                    'is_leasing': 'balance',
                }
                type_operation = type_operation_mapping.get(
                    instance.payment_type
                )

                if not type_operation:
                    raise ValueError(
                        f"Неизвестный тип оплаты: {instance.payment_type}"
                    )

                order_operation = OrderOperation.objects.create(
                    user=instance.user,
                    order_id=instance,
                    type_operation=type_operation
                )
                logger.info(
                    f"Создана запись в OrderOperation для заказа {instance.number}."
                )

                AllOperation.objects.create(
                    user=instance.user,
                    amount=instance.amount,
                    type_operation='order',
                    status_operation='pending',
                    details={
                        'operation_id': str(order_operation.order_operation_id),
                        'type': 'Заказ',
                        'order_number': instance.number,
                    }
                )
                logger.info(f"Создана запись в AllOperation для заказа {instance.number}.")

                product = instance.product
                if product.availability:
                    product.availability = 'on_order'
                    product.save()
                    logger.info(
                        f"Статус товара {product.name} изменен на 'availability = on_order'."
                    )

        except Exception as e:
            logger.error(
                f"Ошибка при создании связанных операций для заказа {instance.number}: {e}"
            )
            raise


@receiver(post_delete, sender=Order)
def restore_product_stock(sender, instance, **kwargs):
    """
    Возвращает товар в наличие при удалении заказа.
    """
    product = instance.product
    if not product.availability:
        product.availability = 'in_stock'
        product.save()
        logger.info(f"Товар {product.name} возвращен в наличие.")


@receiver(post_save, sender=Withdrawal)
def update_user_balance(sender, instance, **kwargs):
    """
    Обновляет баланс пользователя при изменении статуса операции.
    """
    try:
        with transaction.atomic():
            balance, _ = Balance.objects.select_for_update().get_or_create(
                user=instance.user
            )

            if isinstance(instance, Replenishment):
                amount = instance.amount_replenishment
            elif isinstance(instance, Withdrawal):
                amount = instance.amount_withdrawal

            if instance.status_operation == 'success' and not hasattr(
                instance, '_balance_updated'
            ):
                balance.cash_account += amount if isinstance(
                    instance, Replenishment
                ) else -amount
                balance.save()
                instance._balance_updated = True
                logger.info(
                    f"Успешно обновлен баланс пользователя {instance.user.username}"
                )

            elif instance.status_operation == 'failure':
                balance.cash_account -= amount if isinstance(
                    instance, Replenishment
                ) else +amount
                balance.save()
                logger.info(
                    f"Баланс пользователя {instance.user.username} скорректирован после отмены операции."
                )

    except Exception as e:
        logger.error(f"Ошибка при обновлении баланса: {e}")
        raise


@receiver(post_save, sender=CustomUser)
def create_balance(sender, instance, created, **kwargs):
    """Создает баланс новым пользователям."""
    if created:
        Balance.objects.get_or_create(user=instance)

@receiver(post_save, sender=AllOperation)
def update_replenishment_on_all_operation_change(sender, instance, **kwargs):
    """
    Обновляет запись в Replenishment при изменении статуса в AllOperation.
    """
    try:
        logger.info(
            f"Сигнал update_replenishment_on_all_operation_change вызван для {instance}"
        )
        with transaction.atomic():
            replenishment = Replenishment.objects.filter(
                operation_id=instance.operation_id
            ).first()
            if replenishment:
                if replenishment.status_operation != instance.status_operation:
                    replenishment.status_operation = instance.status_operation
                    replenishment.save()
                    logger.info(
                        f"Статус операции {instance.operation_id} обновлен в Replenishment."
                    )

    except Exception as e:
        logger.error(f"Ошибка при обновлении записи в Replenishment: {e}")
        raise


@receiver(post_save, sender=AllOperation)
def update_withdrawal_on_all_operation_change(sender, instance, **kwargs):
    """
    Обновляет запись в Withdrawal при изменении статуса в AllOperation.
    """
    try:
        logger.info(
            f"Сигнал update_withdrawal_on_all_operation вызван для {instance}"
        )
        with transaction.atomic():
            withdrawal = Withdrawal.objects.filter(
                withdrawal_operation_id=instance.operation_id
            ).first()
            if withdrawal:
                if withdrawal.status_operation != instance.status_operation:
                    withdrawal.status_operation = instance.status_operation
                    withdrawal.save()
                    logger.info(
                        f"Статус операции {instance.operation_id} \ "
                        " обновлен в Withdrawal."
                    )
    except Exception as e:
        logger.error(f"Ошибка при обновлении записи в Withdrawal: {e}")
        raise


@receiver(post_save, sender=AllOperation)
def publish_all_operation_event(sender, instance, created, **kwargs):
    event_type = "operation.created" if created else "operation.updated"
    publish_operation_event(instance, event_type)
