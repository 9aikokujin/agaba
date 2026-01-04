from django.db import models
from django.db.models import Max
from django.forms import ValidationError
from django.utils import timezone

from products.models import Product, Company, AdditionalOption, Dimensions
from account.models import CustomUser


class Order(models.Model):
    """Модель для хранения заказов."""

    number = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        verbose_name="Номер заказа",
        db_index=True
    )
    product = models.ForeignKey(
        Product, related_name='orders',
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, verbose_name="Покупатель",
        related_name='order_set',
    )
    date_created = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания заказа"
    )
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL,
        null=True, verbose_name="Организация"
    )
    ORDER_STAGES = [
        ('Stage_1', 'Подготовка документов'),
        ('Stage_2', 'Внесение аванса'),
        ('Stage_3', 'Выдача товара'),
        ('Stage_4', 'Заказ отгружен'),
    ]
    stage = models.CharField(
        max_length=7,
        choices=ORDER_STAGES,
        default='Stage_1',
        verbose_name="Этап заказа"
    )
    selected_additional_options = models.ManyToManyField(
        AdditionalOption,
        blank=True,
        verbose_name="Выбранные опции"
    )
    ORDER_PAYMENT_TYPES = [
        ('is_leasing', 'Лизинг'),
        ('is_cash', 'Безналичный расчет'),
    ]
    payment_type = models.CharField(
        max_length=10,
        choices=ORDER_PAYMENT_TYPES,
        verbose_name="Тип оплаты"
    )
    down_payment_percent = models.IntegerField(
        null=False, blank=False, default=10,
        verbose_name="Первоначальный взнос, %"
    )
    bank_for_leasing = models.ForeignKey(
        'Bank', on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Банк для лизинга"
    )
    first_payment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=False,
        blank=False,
        verbose_name="Сумма первоначального взноса"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Сумма заказа'
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Адрес доставки"
    )
    delivery_number = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        verbose_name="Номер доставки",
        db_index=True
    )
    turnover = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True, null=True,
        verbose_name="Оборот"
    )
    count_of_contracts = models.IntegerField(
        blank=True, null=True,
        verbose_name="Количество контрактов"
    )
    amount_of_leasing = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True, null=True,
        verbose_name="Сумма покупки на лизинг"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def clean(self):
        if self.payment_type == 'is_leasing':
            errors = {}
            if not self.turnover:
                errors['turnover'] = """
                Обязательное поле при типе оплаты лизинг
                """
            if not self.count_of_contracts:
                errors['count_of_contracts'] = """
                Обязательное поле при типе оплаты лизинг
                """
            if not self.amount_of_leasing:
                errors['amount_of_leasing'] = """
                Обязательное поле при типе оплаты лизинг
                """

            if errors:
                raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Переопределение метода save для автоматической
        генерации номера заказа и номера доставки.
        """
        # Генерация уникального номера заказа
        # (формат: ZB000001001 или ZL000001001)
        if not self.number:  # Если номер заказа еще не задан
            # Определяем префикс на основе типа оплаты
            if self.payment_type == 'is_cash':  # Безналичный расчет
                prefix = "ZB"
            elif self.payment_type == 'is_leasing':  # Лизинг
                prefix = "ZL"
            else:
                raise ValueError(
                    "Неверный тип оплаты для формирования номера заказа."
                )

            # Находим максимальный номер среди
            # существующих заказов с таким же префиксом
            last_order = Order.objects.filter(
                number__startswith=prefix
            ).aggregate(
                max_number=Max('number')
            )['max_number']

            if last_order:
                # Извлекаем числовой суффикс из номера последнего заказа
                # Убираем префикс (первые 2 символа)
                last_number = int(last_order[2:])
            else:
                # Если заказов с таким префиксом еще нет, начинаем с 000001001
                last_number = 1001

            # Генерируем следующий номер
            next_number = last_number + 1
            self.number = f"{prefix}{next_number:09d}"

        # Генерация уникального номера доставки (формат: D000000001)
        if not self.delivery_number:  # Если номер доставки еще не задан
            last_delivery = Order.objects.filter(
                delivery_number__startswith="D"
            ).aggregate(
                max_delivery_number=Max('delivery_number')
            )['max_delivery_number']

            if last_delivery:
                last_delivery_number = int(last_delivery[1:])
            else:
                # Если доставок еще нет, начинаем с 000000001
                last_delivery_number = 1

            next_delivery_number = last_delivery_number + 1
            self.delivery_number = f"D{next_delivery_number:09d}"

        super().save(*args, **kwargs)

    def get_selected_additional_options(self):
        """
        Возвращает QuerySet с выбранными дополнительными опциями.
        """
        if self.selected_additional_options:
            return AdditionalOption.objects.filter(
                id__in=self.selected_additional_options
            )
        return AdditionalOption.objects.none()

    def get_manager(self):
        """
        Возвращает ответственного менеджера для заказа.
        """
        assignment = getattr(self, 'manager_assignment', None)
        return assignment.manager if assignment else None

    get_manager.short_description = ("Ответственный менеджер")


class OrderManagerAssignment(models.Model):
    """
    Модель для связи заказа с ответственным менеджером.
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='manager_assignment',
        verbose_name="Заказ"
    )
    manager = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        verbose_name="Ответственный менеджер"
    )
    assigned_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата назначения"
    )

    class Meta:
        verbose_name = "Назначение менеджера"
        verbose_name_plural = "Назначения менеджеров"

    def __str__(self):
        return f"Заказ {self.order.number} назначен менеджеру {self.manager}"


class DeliveryOrder(models.Model):
    """Модель для хранения информации о доставке товара."""
    DELIVERY_STAGES = [
        ('Stage_1', 'Ожидание оплаты'),
        ('Stage_2', 'В пути'),
        ('Stage_3', 'Отгрузка'),
        ('Cancel', 'Отмена'),
    ]
    DELIVERY_TYPES = [
        ('trall', 'Тралл'),
        ('train', 'ЖД'),
        ('sea', 'Море'),
        ('self', 'Своим ходом'),
    ]
    number = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        verbose_name="Номер заказа",
        db_index=True
    )
    date_created = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания заказа"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Получатель"
    )
    delivery_stage = models.CharField(
        max_length=100,
        choices=DELIVERY_STAGES,
        default='Stage_1',
        verbose_name="Этап заказа"
    )
    delivery_type = models.CharField(
        max_length=100,
        choices=DELIVERY_TYPES,
        default='trall',
        verbose_name="Тип доставки"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Сумма заказа'
    )
    dimensions = models.ForeignKey(
        Dimensions,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Габариты"
    )
    date_delivery = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата доставки"
    )
    cargo = models.ForeignKey(
        Product, related_name='cargos',
        on_delete=models.CASCADE, verbose_name="Товар"
    )
    company = models.ForeignKey(
        Company, related_name='delivery_companies',
        on_delete=models.CASCADE, verbose_name="Компания",
        default=''
    )
    address_delivery = models.CharField(
        max_length=255, verbose_name="Адрес доставки"
    )
    order = models.ForeignKey(
        Order, related_name='deliveries',
        on_delete=models.CASCADE, verbose_name="Заказ"
    )

    class Meta:
        verbose_name = "Доставка заказа"
        verbose_name_plural = "Доставки заказов"


class Bank(models.Model):
    """Модель банка для лизинга."""

    name = models.TextField(
        max_length=255,
        verbose_name="Название банка"
    )
    max_sum = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Максимальная сумма лизинга"
    )
    percentage_year = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Удорожание в год в процентах"
    )
    first_installment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Первоначального взноса в процентах"
    )
    logo = models.ImageField(
        upload_to='banks',
        verbose_name="Логотип банка"
    )

    class Meta:
        verbose_name = "Банк для лизинга"
        verbose_name_plural = "Банки для лизинга"

    def __str__(self):
        return self.name
# {
#     "product": 4,
#     "selected_options": [1, 2],
#     "payment_type": "is_cash",
#     "address": "Moscow",
#     "down_payment_percent": 10,
#     "company": 1
# }
