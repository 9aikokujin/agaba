import logging
import uuid
from django.db import models
from django.utils.timezone import now, localtime
from django.db.models.signals import post_save

from account.models import CustomUser, Company
from order.models import Order

from django_app.services import send_notification

logger = logging.getLogger(__name__)

# ЗДЕСЬ НЕ ХВАТАЕТ МОДЕЛИ ДЛЯ ОТВЕТСТВЕННОГО ЛИЦА (БУХ) ДЛЯ ОПЕРАЦИЙ
# тот кто изменяет статус операций.


class BaseModel(models.Model):
    """
    Базовый класс для всех моделей.
    Содержит общие методы и свойства.
    """
    class Meta:
        abstract = True

    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    @property
    def time_since_creation(self):
        """
        Возвращает время с момента создания объекта
        в формате 'X дней, Y часов, Z минут'.
        Если объект ещё не создан (date_created is None),
        возвращает строку "Не создано".
        """
        if self.date_created is None:
            return "Не создано"

        delta = now() - self.date_created
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days} дней, {hours} часов, {minutes} минут"

    def formatted_date(self):
        """Форматирует дату создания объекта."""
        return localtime(self.date_created).strftime('%d.%m.%Y %H:%M')

    formatted_date.short_description = 'Дата создания'
    formatted_date.admin_order_field = 'date_created'


class Balance(models.Model):
    """Модель для хранения баланса пользователя."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        unique=True,
        related_name='balance'
    )
    cash_account = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Счет пользователя'
    )
    date_update = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'

    def __str__(self):
        return f"Баланс {
            self.user.username if self.user else 'неизвестен'
        } - {self.cash_account}"


class Replenishment(BaseModel):
    """Пополнение баланса пользователя."""

    PAYMENT_TYPES = (
        ('account', 'Перевод по счёту'),
        ('card', 'Карта'),
        ('bonus', 'Бонус'),
    )
    STATUS_OPERATIONS = (
        ('pending', 'Ожидание'),
        ('success', 'Пополнен'),
        ('failure', 'Отказ'),
    )

    operation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID Операции пополнения'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    amount_replenishment = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=False, null=False, verbose_name='Сумма пополнения'
    )
    payment_type = models.CharField(
        choices=PAYMENT_TYPES,
        max_length=50,
        default='account',  # пока что по дефолту вывод средств на счет
        verbose_name='Тип операции пополнения',
    )
    status_operation = models.CharField(
        max_length=20,
        choices=STATUS_OPERATIONS,
        default='pending',
        verbose_name='Статус операции пополнения'
    )
    number_transaction = models.CharField(
        blank=True, null=True,
        max_length=100, verbose_name='Номер транзакции'
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='replenishments',
        verbose_name='Компания'
    )

    class Meta:
        verbose_name = 'Пополнение'
        verbose_name_plural = 'Пополнения'
        ordering = ['-date_created']

    # def save(self, *args, **kwargs):
    #     """
    #     Переопределенный метод save для отправки
    #     уведомлений при изменении статуса.
    #     """
    #     is_new = not self.pk  # Проверяем, является ли объект новым
    #     if not is_new:
    #         previous_status = Replenishment.objects.get(
    #             pk=self.pk
    #         ).status_operation
    #     else:
    #         previous_status = None

    #     super().save(*args, **kwargs)  # Вызываем родительский метод save

    #     if not is_new and self.status_operation != previous_status:
    #         # Отправляем уведомление, если статус изменился
    #         send_notification(
    #             user_id=self.user.id,
    #             message_type='replenishment_status_updated',
    #             data={
    #                 'operation_id': str(self.operation_id),
    #                 'previous_status': previous_status,
    #                 'new_status': self.status_operation,
    #                 'timestamp': str(self.date_modified)
    #             }
    #         )

    def mark_as_success(self):
        """Переводим операцию в статус 'success'."""
        if self.status_operation != 'pending':
            raise ValueError("Операция уже была обработана.")
        if self.amount_replenishment <= 0:
            raise ValueError("Сумма пополнения должна быть больше нуля.")
        self.status_operation = 'success'
        self.save()

    def mark_as_failure(self):
        """Переводим операцию в статус 'failure'."""
        if self.status_operation != 'pending':
            raise ValueError("Операция уже была обработана.")
        self.status_operation = 'failure'
        self.save()

    def __str__(self):
        username = self.user.username if self.user else "Пользователь удален"
        return f'{username} пополнил свой баланс на {
            self.amount_replenishment
        }'


class Withdrawal(BaseModel):
    """Вывод средств пользователя."""

    TYPES_OPERATIONS = (
        ('account', 'Вывод на счёт'),
        ('card', 'Вывод на карту'),
    )
    STATUS_OPERATIONS = (
        ('pending', 'Ожидание'),
        ('success', 'Выполнен'),
        ('failure', 'Отказ'),
    )

    withdrawal_operation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        editable=False, unique=True,
        verbose_name='ID Операции вывода'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    amount_withdrawal = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=False, null=False,
        verbose_name='Сумма вывода'
    )
    type_operation = models.CharField(
        choices=TYPES_OPERATIONS,
        max_length=max(map(lambda x: len(x[0]), TYPES_OPERATIONS)),
        verbose_name='Тип операции вывода',
        default='account'
    )
    status_operation = models.CharField(
        max_length=20,
        choices=STATUS_OPERATIONS,
        default='pending',
        verbose_name='Статус операции вывода'
    )
    number_account = models.CharField(
        max_length=100, blank=True,
        null=True, verbose_name='Номер счёта'
    )
    inn = models.CharField(
        max_length=100, blank=True,
        null=True, verbose_name='ИНН'
    )
    bik = models.CharField(
        max_length=100, blank=True,
        null=True, verbose_name='БИК'
    )
    ks = models.CharField(
        max_length=100, blank=True,
        null=True, verbose_name='КС'
    )
    rs = models.CharField(
        max_length=100, blank=True,
        null=True, verbose_name='РС'
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='withdrawals',
        verbose_name='Компания'
    )

    class Meta:
        verbose_name = 'Вывод средств'
        verbose_name_plural = 'Выводы средств'

    # def save(self, *args, **kwargs):
    #     """
    #     Переопределенный метод save для
    #     отправки уведомлений при изменении статуса.
    #     """
    #     is_new = not self.pk  # Проверяем, является ли объект новым
    #     if not is_new:
    #         previous_status = Withdrawal.objects.get(
    #             pk=self.pk
    #         ).status_operation
    #     else:
    #         previous_status = None

    #     super().save(*args, **kwargs)  # Вызываем родительский метод save

    #     if not is_new and self.status_operation != previous_status:
    #         # Отправляем уведомление, если статус изменился
    #         send_notification(
    #             user_id=self.user.id,
    #             message_type='replenishment_status_updated',
    #             data={
    #                 'operation_id': str(self.withdrawal_operation_id),
    #                 'previous_status': previous_status,
    #                 'new_status': self.status_operation,
    #                 'timestamp': str(self.date_modified)
    #             }
    #         )

    def mark_as_success(self):
        """Переводим операцию в статус 'success'."""
        if self.status_operation != 'pending':
            raise ValueError("Операция уже была обработана.")
        if self.amount_withdrawal <= 0:
            raise ValueError("Сумма вывода должна быть больше нуля.")
        self.status_operation = 'success'
        self.save()

    def mark_as_failure(self):
        """Переводим операцию в статус 'failure'."""
        if self.status_operation != 'pending':
            raise ValueError("Операция уже была обработана.")
        self.status_operation = 'failure'
        self.save()

    def __str__(self):
        username = self.user.username if self.user else "Пользователь удален"
        return f'{username} вывел {self.amount_withdrawal}'


class OrderOperation(BaseModel):
    """Операции по заказам."""
    # Придумать что то со статусом
    TYPES_OPERATIONS = (
        ('account', 'Счёт'),
        ('card', 'Карта'),
        ('balance', 'Баланс'),
    )

    order_operation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        editable=False, verbose_name='ID Операции'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    order_id = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='ID Заказа'
    )
    type_operation = models.CharField(
        choices=TYPES_OPERATIONS,
        max_length=max(map(lambda x: len(x[0]), TYPES_OPERATIONS)),
        verbose_name='Тип оплаты'
    )

    class Meta:
        verbose_name = 'Операция по заказам'
        verbose_name_plural = 'Операции по заказам'
        ordering = ['-date_created']

    def __str__(self):
        order_number = self.order_id.number if self.order_id else "Заказ удален"
        return (
            f'Пользователь {self.user.username} оформил заказ '
            f'Номер: {order_number}, Тип оплаты {self.type_operation}.'
        )


class AllOperation(BaseModel):
    """Модель для хранения Всех операций."""

    OPERATION_TYPES = (
        ('replenishment', 'Пополнение'),
        ('withdrawal', 'Вывод'),
        ('order', 'Заказ'),
    )
    STATUS_OPERATIONS = (
        ('success', 'Успешно'),
        ('failure', 'Отказ'),
        ('pending', 'Ожидание'),
    )
    PAYMENT_TYPES = (
        ('card', 'Карта'),
        ('bonus', 'Бонус'),
        ('account', 'Перевод по счёту'),
    )
    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_TYPES,
        verbose_name='Способ оплаты',
        default='account'
    )
    operation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID операции'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Сумма операции'
    )
    type_operation = models.CharField(
        max_length=50,
        choices=OPERATION_TYPES,
        verbose_name='Тип операции'
    )
    status_operation = models.CharField(
        max_length=20,
        choices=STATUS_OPERATIONS,
        verbose_name='Статус операции',
        default='pending'
    )
    replenishment = models.ForeignKey(
        Replenishment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Пополнение'
    )
    withdrawal = models.ForeignKey(
        Withdrawal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Вывод'
    )
    order_operation = models.ForeignKey(
        OrderOperation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Операция по заказу'
    )
    details = models.JSONField(
        default=dict,
        verbose_name='Детали операции'
    )
    related_operations = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name='Связанные операции'
    )
    date_modified = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения'
    )

    class Meta:
        verbose_name = 'Все операции'
        ordering = ['-date_created']

    def __str__(self):
        return f"""
        Пользователь: {self.user.username}
        выполнил операцию {self.get_type_operation_display()},
         статус: {self.get_status_operation_display()}
        """

    def save(self, *args, **kwargs):
        """
        Переопределенный метод save с защитой от рекурсии.
        """
        if getattr(self, '_skip_save_logic', False):
            return super().save(*args, **kwargs)

        is_new = not self.pk
        if not is_new:
            try:
                previous_status = AllOperation.objects.get(
                    pk=self.pk
                ).status_operation
            except AllOperation.DoesNotExist:
                previous_status = None
        else:
            previous_status = None

        try:
            self._skip_save_logic = True
            super().save(*args, **kwargs)
        finally:
            self._skip_save_logic = False

        if not is_new and self.status_operation != previous_status:
            send_notification(
                user_id=self.user.id,
                message_type='operation_status_updated',
                data={
                    'operation_id': str(self.operation_id),
                    'previous_status': previous_status,
                    'new_status': self.status_operation,
                    'timestamp': str(self.date_modified)
                }
            )

            for operation in self.related_operations.all():
                operation.status_operation = self.status_operation
                operation.save()
                logger.info(
                    f"Статус операции {operation.id} обновлен на {
                        self.status_operation
                    }"
                    )

                if operation.type_operation == 'replenishment':
                    post_save.send(
                        Replenishment,
                        instance=operation,
                        created=False
                    )
                elif operation.type_operation == 'withdrawal':
                    post_save.send(
                        Withdrawal,
                        instance=operation,
                        created=False
                    )


class AccountPDF(models.Model):
    """Модель для сохранения PDF файлов с счетом."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    path_invoice = models.FileField(
        blank=True, upload_to='invoice/',
        verbose_name='Путь к файлу счёта'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    download_link = models.URLField(
        blank=True, null=True
    )

    class Meta:
        verbose_name = 'PDF файл счёта'
        verbose_name_plural = 'PDF файлы счёта'
        ordering = ['-id']

    def __str__(self):
        return f"PDF файл счёта пользователя {self.user.username}"
