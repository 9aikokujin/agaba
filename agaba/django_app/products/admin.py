from datetime import datetime

from django.contrib import admin
from .models import (
    Product, PriceHistory, Category, Subcategory, Attribute,
    ProductAttribute, ProductDocument, ProductPhoto, Dimensions,
    AdditionalOption, Question, Answer, Comparison, ProductReview, Favorite
)


class PriceHistoryInline(admin.TabularInline):
    """Админ панель для модели История цены."""
    model = PriceHistory
    extra = 0
    readonly_fields = ('changed_at',)


class ProductAttributeInline(admin.TabularInline):
    """Админ панель для модели Атрибуты продукта."""
    model = ProductAttribute
    extra = 1


class ProductDocumentInline(admin.TabularInline):
    """Админ панель для модели Документы продукта."""
    model = ProductDocument
    extra = 1


class ProductPhotoInline(admin.TabularInline):
    """Админ панель для модели Фото продукта."""
    model = ProductPhoto
    extra = 1


class DimensionsInline(admin.StackedInline):
    """Админ панель для модели Размеры продукта."""
    model = Dimensions
    max_num = 1


class AdditionalOptionInline(admin.TabularInline):
    """Админ панель для модели Доп. опции продукта."""
    model = AdditionalOption
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админ панель для модели Продукт."""
    list_display = (
        'name', 'brand', 'cur_price', 'prev_price',
        'status', 'availability', 'created_at'
    )
    list_filter = (
        'status', 'availability', 'category',
        'subcategory', 'condition'
    )
    search_fields = ('name', 'brand', 'description')
    date_hierarchy = 'created_at'
    inlines = [
        PriceHistoryInline,
        ProductAttributeInline,
        ProductDocumentInline,
        ProductPhotoInline,
        DimensionsInline,
        AdditionalOptionInline
    ]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': (
                'brand', 'name', 'slug', 'description',
                'cur_price', 'prev_price'
            )
        }),
        ('Классификация', {
            'fields': ('category', 'subcategory')
        }),
        ('Дополнительная информация', {
            'fields': (
                'author', 'company', 'year_of_release', 'condition'
            )
        }),
        ('Параметры продажи', {
            'fields': (
                'delivery_time', 'availability', 'location', 'min_deposit'
            )
        }),
        ('Медиа', {
            'fields': ('video_url',)
        }),
        ('Статус', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ панель для модели Категории продукта."""
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Админ панель для модели Подкатегории продукта."""
    list_display = ('name', 'category', 'slug')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    """Админ панель для модели Атрибут категории."""
    list_display = ('name', 'subcategory')
    list_filter = ('subcategory',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Админ панель для модели Вопросы продукта."""
    list_display = ('product', 'username', 'text_short', 'date')
    list_filter = ('product', 'date')
    search_fields = ('text', 'username__username')

    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Текст вопроса'


class AnswerInline(admin.StackedInline):
    """Инлайн форма для модели Ответы продукта."""
    model = Answer
    extra = 1


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Админ панель для модели Ответы продукта."""
    list_display = ('question', 'user', 'text_short', 'date')
    list_filter = ('product', 'date')
    search_fields = ('text', 'user__username')

    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Текст ответа'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Админ панель для модели Отзывы продукта."""
    list_display = ('product', 'user', 'rating', 'created_at', 'status')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('comment', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ панель для модели Избранное."""
    list_display = ('product', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'user__username')


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    """Админ панель для модели Срванение."""
    list_display = ('user', 'session_key', 'timestamp_formatted')
    list_filter = ('timestamp',)
    search_fields = ('product__name', 'user__username')

    def timestamp_formatted(self, obj):
        return datetime.fromtimestamp(
            obj.timestamp
        ).strftime('%Y-%m-%d %H:%M:%S')
    timestamp_formatted.short_description = 'Время сравнения'
