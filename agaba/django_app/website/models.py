# import os
# import time
# from datetime import datetime
# from django.db import models
# from django.core.validators import MinValueValidator, MaxValueValidator

# from api.utils import delete_from_minio
# from account.models import CustomUser, Company
# from .storage import UUIDFileSystemStorage
# from .utils import (
#     calculate_file_hash,
# )
# from django.db import transaction
# from django.utils.text import slugify
# from unidecode import unidecode
# import random
# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db.models import Q
# from functools import reduce
# from operator import or_


# TYPE_CHOICES = (
#     ('text', 'text'),
#     ('radio', 'radio'),
#     ('dropdown', 'dropdown'),
#     # ('text_multiline', 'text_multiline'),
# )


# class Category(models.Model):
#     """Модель для хранения категорий (групп) товаров."""
#     name = models.CharField(
#         max_length=100, unique=True, verbose_name='Наименование')
#     slug = models.SlugField(unique=True, blank=True)
#     # Родительская категория
#     # (если None, то это корневая категория)
#     parent = models.ForeignKey(
#         'self', on_delete=models.CASCADE, null=True, blank=True,
#         related_name='children', verbose_name='Родительская категория')
#     image = models.ImageField(
#         upload_to='subgroup_images/', null=True, blank=True)
#     svg_icon = models.TextField(
#         null=True, blank=True, verbose_name='SVG иконка')
#     # Если True, то категория является терминальной
#     # (т.е. не имеет дочерних категорий)
#     # и используется только для хранения товаров
#     # Если False, то категория может иметь дочерние категории
#     # и используется для группировки товаров
#     # в более крупные группы
#     is_terminal = models.BooleanField(
#         default=True, verbose_name='Терминальная категория',
#         help_text='Отметьте, если категория используется' \
#         'только для хранения товаров и не имеет дочерних категорий.'
#     )

#     def save(self, *args, **kwargs):
#         if not self.slug:  # Only generate slug if it's not already set
#             self.slug = slugify(unidecode(self.name))
#             # Check if the slug already exists
#             while Category.objects.filter(slug=self.slug).exists():
#                 # Append a random 5-digit number to the slug
#                 self.slug = f"{self.slug}_{random.randint(10000, 99999)}"

#         # Проверка глубины дерева
#         if self.get_level() > 1:
#             raise ValidationError(
#                 "Глубина дерева категорий не может превышать двух уровней.")

#         super().save(*args, **kwargs)

#     def get_ancestors(self):
#         """Возвращает список всех предков текущей категории."""
#         ancestors = []
#         current = self
#         while current.parent:
#             ancestors.append(current.parent)
#             current = current.parent
#         return list(reversed(ancestors))

#     def get_level(self):
#         """
#         Возвращает уровень категории в дереве.
#         Уровень корневой категории равен 0.
#         """
#         level = 0
#         current = self
#         while current.parent:
#             level += 1
#             current = current.parent
#         return level

#     def get_terminal_categories(self):
#         """
#         Возвращает список всех терминальных категорий, включая текущую, если она терминальная.
#         """
#         terminal_categories = []
#         if self.is_terminal:
#             terminal_categories.append(self)
#         else:
#             # Recursively get terminal categories from children
#             for child in self.children.all():
#                 terminal_categories.extend(child.get_terminal_categories())
#         return terminal_categories

#     def get_products(self):
#         """
#         Возвращает QuerySet всех продуктов из всех терминальных категорий,
#         включая текущую, если она терминальная.
#         """
#         # Import Product model to avoid circular imports
#         from .models import Product

#         # Get all terminal categories
#         terminal_categories = self.get_terminal_categories()

#         # Create a list of Q objects for filtering products by terminal categories
#         q_objects = [Q(category=category) for category in terminal_categories]

#         # Combine Q objects using the OR operator
#         if q_objects:
#             combined_query = reduce(or_, q_objects)
#             return Product.objects.filter(combined_query)
#         else:
#             # Return an empty queryset if no terminal categories exist
#             return Product.objects.none()

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = 'Категория товаров'
#         verbose_name_plural = 'Категории товаров'


# class Product(models.Model):
#     """Модель товара."""
#     brand = models.CharField(max_length=255, verbose_name='Марка')
#     name = models.CharField(
#         max_length=255, unique=True, verbose_name='Наименование')
#     slug = models.SlugField(unique=True, blank=True)
#     description = models.TextField(
#         max_length=5000, default="",
#         verbose_name='Описание'
#     )
#     # Аккаунт продавца, создающего товар
#     author = models.ForeignKey(
#         CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Автор")
#     # Компания-продавец (одна из связанных с автором)
#     selling_company = models.ForeignKey(
#         Company, on_delete=models.SET_NULL,
#         null=True, blank=True, verbose_name="Продает компания")
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     category = models.ForeignKey(
#         Category, on_delete=models.CASCADE, related_name='products')
#     prod_year = models.IntegerField(
#         null=False, blank=False,
#         default=datetime.now().year,
#         verbose_name="Год производства"
#     )
#     condition = models.CharField(
#         max_length=25,
#         choices=[
#             ('new', 'Новое'),
#             ('used', 'Б/у'),
#             ('spare_parts', 'На з/ч')
#         ],
#         default='new',
#         verbose_name="Состояние"
#     )
#     delivery_time_days = models.IntegerField(
#         null=False, blank=False, default=14,
#         verbose_name="Срок доставки"
#     )
#     in_stock = models.BooleanField(
#         default=True, verbose_name="В наличии"
#     )
#     location = models.CharField(
#         max_length=255,
#         verbose_name='Местонахождение товара',
#         default="Москва"
#     )
#     min_down_payment_percentage = models.IntegerField(
#         verbose_name="Минимальный первый взнос %",
#         validators=[
#             MinValueValidator(0),
#             MaxValueValidator(100)
#         ],
#         default=10,
#     )
#     mod_status = models.CharField(
#         max_length=25,
#         choices=[('on_mod', 'На модерации'), ('active', 'Активный'),
#                  ('rejected', 'Отклонен'), ('withdrawn', 'Снят с продажи')],
#         default='active', verbose_name="Статус модерации")
#     video_link = models.URLField(
#         max_length=255, blank=True, null=True, verbose_name="Ссылка на видео")

#     # Габариты и масса
#     length = models.IntegerField(
#         verbose_name='Длина, мм', blank=True, null=True)
#     width = models.IntegerField(
#         verbose_name='Ширина, мм', blank=True, null=True)
#     height = models.IntegerField(
#         verbose_name='Высота, мм', blank=True, null=True)
#     weight = models.IntegerField(
#         verbose_name='Масса, кг', blank=True, null=True)

#     class Meta:
#         verbose_name = "Товар"
#         verbose_name_plural = "Товары"

#     # @property
#     # def price_history(self):
#     #     # Cache the queryset to avoid repeated database queries
#     #     if not hasattr(self, '_cached_price_history'):
#     #         self._cached_price_history = self.prices.all().order_by('-date') # Uses the default ordering
#     #     return self._cached_price_history

#     @property
#     def price_history(self):
#         return self.prices.all().order_by('-date')

#     @property
#     def cur_price(self):
#         # Fetch the latest price
#         latest_price = self.price_history.first()
#         return latest_price.price if latest_price else None

#     @property
#     def old_price(self):
#         # Fetch the second latest price
#         prices = list(self.price_history[:2])  # Fetch only the first two records
#         return prices[1].price if len(prices) > 1 else None

#     @property
#     def price_diff(self):
#         # Calculate the difference between current and old price
#         cur_price = self.cur_price
#         old_price = self.old_price
#         if cur_price is not None and old_price is not None:
#             return cur_price - old_price
#         return None

#     @property
#     def questions(self):
#         return self.question_set.all()  # Возвращает все вопросы для текущего продукта

#     def save(self, *args, **kwargs):
#         if not self.slug:  # Only generate slug if it's not already set
#             self.slug = slugify(unidecode(self.name))
#             # Check if the slug already exists
#             while Product.objects.filter(slug=self.slug).exists():
#                 # Append a random 5-digit number to the slug
#                 self.slug = f"{self.slug}_{random.randint(10000, 99999)}"
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.brand} - {self.name}"


# class Price(models.Model):
#     """Модель цены товара в данный момент."""
#     product = models.ForeignKey(
#         'Product', on_delete=models.CASCADE, related_name='prices')
#     price = models.DecimalField(
#         max_digits=15, decimal_places=0, verbose_name='Цена')
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.product.name} - {self.price}"

#     class Meta:
#         verbose_name = 'Цена'
#         verbose_name_plural = 'Цены'


# class UnitOfMeasurement(models.Model):
#     """Модель единицы измерения свойства товара."""
#     name = models.CharField(
#         max_length=100, verbose_name='Название единицы измерения')
#     abbr = models.CharField(
#         max_length=20, verbose_name='Сокращение', blank=True, null=True)

#     def __str__(self):
#         return f"{self.name} ({self.abbr})"

#     class Meta:
#         verbose_name = 'Единица измерения'
#         verbose_name_plural = 'Единицы измерений'


# class AttributeGroup(models.Model):
#     """Модель группы атрибутов (свойств, характеристик) товара."""
#     category = models.ForeignKey(
#         Category, on_delete=models.CASCADE, related_name='attribute_groups')
#     name = models.CharField(max_length=255)

#     def __str__(self):
#         return self.name


# class AttributeTemplate(models.Model):
#     """Модель шаблона атрибута (свойства, характеристики) товара."""
#     # Хранит шаблон характеристик товара в БД
#     # Используется для создания характеристик товара в форме или ендпойнте
#     group = models.ForeignKey(
#         AttributeGroup, on_delete=models.CASCADE, related_name='templates')
#     type = models.CharField(
#         max_length=25, choices=TYPE_CHOICES, verbose_name="Тип атрибута")
#     name = models.CharField(max_length=255)
#     desc = models.CharField(max_length=255, null=True, blank=True)
#     meas_unit = models.ForeignKey(
#         UnitOfMeasurement, on_delete=models.CASCADE, null=True, blank=True)
#     placeholder = models.CharField(max_length=255, blank=True)
#     json_data = models.JSONField(blank=True, null=True)
#     required = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.type}: {self.name}"


# class Attribute(models.Model):
#     """Модель атрибута (свойства, характеристики) товара."""
#     # Хранит значение атрибута конкретного товара в БД
#     template = models.ForeignKey(
#         AttributeTemplate, related_name='attributes', on_delete=models.CASCADE)
#     product = models.ForeignKey(
#         Product, related_name='attributes', on_delete=models.CASCADE)
#     key = models.CharField(max_length=100, blank=True, null=True)
#     value = models.CharField(max_length=255)

#     class Meta:
#         verbose_name = "Атрибут товара"
#         verbose_name_plural = "Атрибуты товара"

#     def __str__(self):
#         meas_unit_abbr = self.template.meas_unit
#         meas_unit_abbr = f" ({meas_unit_abbr.abbr})" if meas_unit_abbr else ''
#         return f"{self.template.name}: {self.value}{meas_unit_abbr}"


# class ProductImage(models.Model):
#     """Модель изображения товара."""
#     product = models.ForeignKey(
#         Product, related_name='product_images', on_delete=models.CASCADE)
#     image = models.URLField()
#     image_hash = models.CharField(max_length=32, blank=True, editable=False)
#     # Ракурс изображения товара
#     # Нужен для определения ячейки в сетке изображений товара
#     aspect = models.CharField(max_length=50, blank=True, null=True)

#     class Meta:
#         verbose_name = "Изображение товара"
#         verbose_name_plural = "Изображения товара"

#     def delete(self, *args, **kwargs):
#         """
#         Удаляем файл с MinIO перед удалением записи из базы данных.
#         """
#         # Извлекаем имя файла из URL
#         file_name = self.image.split('/')[-1]

#         # Удаляем файл с MinIO
#         delete_from_minio(file_name)

#         # Удаляем запись из базы данных
#         super().delete(*args, **kwargs)

#     def __str__(self):
#         return f"{self.product.name} - {self.aspect}"

#     # def save(self, *args, **kwargs):
#     #     # Calculate the hash of the uploaded image
#     #     self.image_hash = calculate_file_hash(self.image)

#     #     # Защита от дубликатов изображений
#     #     # Очень часто могут быть одинаковые изображения в разных товарах
#     #     # Поэтому нужно проверять, есть ли такое изображение в БД
#     #     # Для экономии места на диске, существующее изображение вновь не
#     #     # сохраняется, а в БД записывается ссылка на существующее изображение
#     #     with transaction.atomic():
#     #         existing_images = ProductImage.objects.filter(
#     #             image_hash=self.image_hash)

#     #         if existing_images.exists():
#     #             print("Image already exists in the database")

#     #             # Get the first existing image
#     #             existing_image = existing_images.first()

#     #             # Check if the image file is missing in the media folder
#     #             image_path = os.path.join(
#     #                 settings.MEDIA_ROOT, existing_image.image.name)
#     #             if not os.path.exists(image_path):
#     #                 print("Image file is missing, saving the new one")

#     #                 # Save the new image
#     #                 # super().save(*args, **kwargs)

#     #                 # Update all existing images to point to the new image file
#     #                 existing_images.update(image=self.image)
#     #             else:
#     #                 # Use the existing image
#     #                 self.image = existing_image.image.name
#     #             super().save(*args, **kwargs)

#     #         else:
#     #             print("Image is unique")
#     #             super().save(*args, **kwargs)


# class ProductDocument(models.Model):
#     """Модель документа о товаре."""
#     product = models.ForeignKey(
#         Product, related_name='product_docs', on_delete=models.CASCADE)
#     doc = models.FileField(
#         upload_to='product_docs/', storage=UUIDFileSystemStorage())
#     doc_hash = models.CharField(max_length=32, blank=True, editable=False)
#     name = models.CharField(
#         max_length=255, verbose_name='Наименование', blank=True,)

#     class Meta:
#         verbose_name = "Документ о товаре"
#         verbose_name_plural = "Документы о товаре"

#     def __str__(self):
#         return self.doc.name

#     def save(self, *args, **kwargs):
#         # Calculate the hash of the uploaded image
#         self.doc_hash = calculate_file_hash(self.doc)

#         doc_name = self.doc.name
#         ext = os.path.splitext(doc_name)[1]

#         if not self.name:
#             self.name = doc_name.strip().replace(' ', '_')
#         else:
#             self.name = self.name.strip().replace(' ', '_') + ext

#         existing_doc = ProductDocument.objects.filter(
#             doc_hash=self.doc_hash).first()
#         if existing_doc:
#             self.doc = existing_doc.doc

#         super().save(*args, **kwargs)


# class AdditionalOption(models.Model):
#     """Модель опции дополнительного товара."""
#     product = models.ForeignKey(
#         Product, related_name='additional_options', on_delete=models.CASCADE)
#     name = models.TextField(max_length=255,  verbose_name='Наименование')
#     price = models.DecimalField(
#         max_digits=15, decimal_places=0, verbose_name='Цена')

#     class Meta:
#         verbose_name = "Опция"
#         verbose_name_plural = "Опции"


# class Question(models.Model):
#     """Модель для хранения вопросов к товарам."""

#     username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     text = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name = 'Вопрос'
#         verbose_name_plural = 'Вопросы'
#         ordering = ['-date']

#     def __str__(self):
#         return self.text[:50]


# class Answer(models.Model):
#     """Модель для хранения ответов на вопросы к товарам."""

#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     question = models.ForeignKey(
#         Question, on_delete=models.CASCADE, related_name='answers')
#     text = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name = 'Ответ'
#         verbose_name_plural = 'Ответы'
#         ordering = ['-date']

#     def __str__(self):
#         return self.text[:50]


# class Comparison(models.Model):
#     """Модель для хранения сравнений товаров"""

#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     # Для авторизованных пользователей
#     user = models.ForeignKey(
#         CustomUser, on_delete=models.CASCADE, null=True, blank=True)
#     # Для анонимных пользователей
#     session_key = models.CharField(max_length=40, null=True, blank=True)
#     timestamp = models.IntegerField(
#         verbose_name="UNIX Время", blank=True, null=True)

#     def save(self, *args, **kwargs):
#         if not self.timestamp:
#             # Преобразуем текущее время в UNIX
#             self.timestamp = int(time.time())
#         super().save(*args, **kwargs)

#     @classmethod
#     def delete_old_entries(cls, days=7):
#         """Удаляет записи старше `days` дней"""
#         threshold = int(time.time()) - (days * 86400)  # 86400 секунд = 1 день
#         cls.objects.filter(timestamp__lt=threshold).delete()


# class ProductReview(models.Model):
#     """Модель для хранения отзывов по товарам."""

#     product = models.ForeignKey(
#         Product, on_delete=models.CASCADE, related_name='product_reviews')
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
#     comment = models.TextField()
#     pros = models.TextField(blank=True, null=True)
#     cons = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     image = models.ImageField(
#         upload_to='product_reviews/',
#         storage=UUIDFileSystemStorage(),
#         blank=True, null=True
#     )
#     visible = models.BooleanField(default=True)

#     def __str__(self):
#         return f"Review by {self.user.username} for {self.product.name}"


# class Favorite(models.Model):
#     """Модель для хранения любимых товаров."""

#     product = models.ForeignKey(
#         Product, on_delete=models.CASCADE, related_name='favorites')
#     user = models.ForeignKey(
#         CustomUser, on_delete=models.CASCADE, related_name='favorites')
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = 'Любимый товар'
#         verbose_name_plural = 'Любимые товары'
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Favorite by {self.user.username} for {self.product.name}"



# # Группа атрибутов (главные характеристики) привязаны к категории товара.
# # 