
import time
from datetime import datetime

from django.db import models
from account.models import CustomUser, Company
from .utils import UUIDFileSystemStorage



class Product(models.Model):
    """Модель товара."""

    STATUS_CHOICES = [
        ('on_moderation', 'На модерации'),
        ('active', 'Активный'),
        ('rejected', 'Отклонен'),
        ('removed', 'Снят с продажи'),
    ]

    CONDITION_CHOICES = [
        ('new', 'Новое'),
        ('used', 'Б/у'),
        ('for_parts', 'На запчасти'),
    ]

    brand = models.CharField(
        max_length=255,
        verbose_name="Бренд"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Наименование"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Слаг"
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    cur_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Текущая цена"
    )
    prev_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        verbose_name="Предыдущая цена"
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Подкатегория"
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='uploaded_products',
        verbose_name="Автор"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Компания"
    )
    year_of_release = models.IntegerField(
        null=False, blank=False,
        default=datetime.now().year,
        verbose_name="Год выпуска"
    )
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        verbose_name="Состояние"
    )
    delivery_time = models.IntegerField(
        verbose_name="Срок доставки (дни)"
    )
    availability = models.CharField(
        max_length=20,
        choices=[
            ('in_stock', 'В наличии'),
            ('on_order', 'Под заказ')
        ], verbose_name="Доступность"
    )
    location = models.CharField(
        max_length=255,
        verbose_name="Местонахождение товара"
    )
    min_deposit = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Минимальный первый взнос"
    )
    video_url = models.URLField(
        blank=True, null=True,
        verbose_name="Ссылка на видео о товаре"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='on_moderation',
        verbose_name="Статус товара"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(0, 6)],
        verbose_name="Рейтинг", default=0
    )

    def save(self, *args, **kwargs):
        """
        ?????????????? ????? save ???:
        1. ?????????? ?????????? ???? ? `prev_price` ??? ????????? `cur_price`.
        2. ?????????? ??????? ??? (`PriceHistory`) ??? ????????? `cur_price`.
        """
        update_fields = kwargs.get("update_fields")
        old_price = None
        if self.pk:
            old_price = Product.objects.filter(
                pk=self.pk
            ).values_list(
                "cur_price", flat=True
            ).first()

        super().save(*args, **kwargs)

        if old_price is None:
            PriceHistory.objects.create(
                product=self,
                price=self.cur_price
            )
            return

        if update_fields is not None and "cur_price" not in update_fields:
            return

        if old_price != self.cur_price:
            self.prev_price = old_price
            Product.objects.filter(
                pk=self.pk
            ).update(prev_price=old_price)
            PriceHistory.objects.create(
                product=self,
                price=self.cur_price
            )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.brand} {self.name}"


class PriceHistory(models.Model):
    """Модель истории цен товара."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='price_history',
        verbose_name="Продукт"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата изменения"
    )

    class Meta:
        verbose_name = "История цен"
        verbose_name_plural = "Истории цен"

    def __str__(self):
        return f"{self.product.name} - {self.price} ({self.changed_at})"


class Category(models.Model):
    """Модель категории товара."""

    name = models.CharField(
        max_length=255,
        verbose_name="Название категории"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Слаг"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    """Модель подкатегории товара."""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name="Категория"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название подкатегории"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Слаг"
    )

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"

    def __str__(self):
        return self.name


class Attribute(models.Model):
    """Модель характеристики товара."""

    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name="Подкатегория"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название характеристики"
    )

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    def __str__(self):
        return f"{self.subcategory.name} - {self.name}"


class ProductAttribute(models.Model):
    """Характеристика отдельного товара."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name="Продукт"
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        verbose_name="Характеристика"
    )
    value = models.CharField(
        max_length=255,
        verbose_name="Значение"
    )

    class Meta:
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товара"

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"


class ProductDocument(models.Model):
    """Документация товара."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Продукт"
    )
    document_url = models.URLField(
        verbose_name="Ссылка на документ"
    )
    description = models.CharField(
        max_length=255, blank=True,
        null=True,
        verbose_name="Описание"
    )

    class Meta:
        verbose_name = "Документация товара"
        verbose_name_plural = "Документации товара"

    def __str__(self):
        return f"Документ для {self.product.name}"


class ProductPhoto(models.Model):
    """Фото товара."""

    POSITION_CHOICES = [
        ('front', 'Спереди'),
        ('back', 'Сзади'),
        ('left', 'Слева'),
        ('right', 'Справа'),
        ('front_left', 'Спереди левый угол'),
        ('front_right', 'Спереди правый угол'),
        ('back_left', 'Сзади левый угол'),
        ('back_right', 'Сзади правый угол'),
        ('other', 'Просто фото'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Продукт"
    )
    image = models.ImageField(
        upload_to='product_photos/',
        verbose_name="Фото"
    )
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        blank=True, null=True,
        verbose_name="Позиция"
    )

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товара"

    def __str__(self):
        return f"Фото {self.position} для {self.product.name}"


class Dimensions(models.Model):
    """Габариты товара."""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='dimensions',
        verbose_name="Продукт"
    )
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Длина"
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ширина"
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Высота"
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Масса"
    )

    class Meta:
        verbose_name = "Габариты товара"
        verbose_name_plural = "Габариты товара"

    def __str__(self):
        return f"Габариты для {self.product.name}"


class AdditionalOption(models.Model):
    """Дополнительные опции товара."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='additional_options',
        verbose_name="Продукт"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название опции"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена опции"
    )

    class Meta:
        verbose_name = "Дополнительная опция"
        verbose_name_plural = "Дополнительные опции"

    def __str__(self):
        return f"{self.name} ({self.price}) для {self.product.name}"


class Question(models.Model):
    """Модель для хранения вопросов к товарам."""

    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-date']

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    """Модель для хранения ответов на вопросы к товарам."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-date']

    def __str__(self):
        return self.text[:50]


class Comparison(models.Model):
    """Модель для хранения сравнений товаров"""

    products = models.ManyToManyField(
        Product,
        related_name='comparisons',
        verbose_name="Продукты"
    )
    # Для авторизованных пользователей
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE,
        null=True, blank=True, unique=True
    )
    # Для анонимных пользователей
    session_key = models.CharField(max_length=40, null=True, blank=True)
    timestamp = models.IntegerField(
        verbose_name="UNIX Время", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.timestamp:
            # Преобразуем текущее время в UNIX
            self.timestamp = int(time.time())
        super().save(*args, **kwargs)

    # @classmethod
    # def delete_old_entries(cls, days=7):
    #     """Удаляет записи старше `days` дней"""
    #     threshold = int(time.time()) - (days * 86400)  # 86400 секунд = 1 день
    #     cls.objects.filter(timestamp__lt=threshold).delete()

    class Meta:
        verbose_name = "Сравнение товаров"
        verbose_name_plural = "Сравнения товаров"


class ProductReview(models.Model):
    """Модель для хранения отзывов по товарам."""

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('moderation', 'Модерация'),
        ('approved', 'Утвержден'),
        ('rejected', 'Отклонен'),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='product_reviews',
        verbose_name="Продукт"
        )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Рейтинг"
    )
    comment = models.TextField(verbose_name="Комментарий")
    pros = models.TextField(blank=True, null=True, verbose_name="Плюсы")
    cons = models.TextField(blank=True, null=True, verbose_name="Минусы")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to='product_reviews/',
        storage=UUIDFileSystemStorage(),
        blank=True, null=True,
        verbose_name="Изображение"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус отзыва"
    )
    order = models.ForeignKey(
        'order.Order', on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Заказ"
    )

    class Meta:
        verbose_name = "Отзыв по товару"
        verbose_name_plural = "Отзывы по товару"

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"


class Favorite(models.Model):
    """Модель для Избранных товаров."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    user__isnull=False
                ) | models.Q(
                    session_key__isnull=False
                ),
                name='favorite_user_or_session'
            ),
        ]

    def __str__(self):
        owner = self.user.username if self.user else (
            self.session_key or "anonymous"
        )
        return f"Favorite by {owner} for {self.product.name}"
