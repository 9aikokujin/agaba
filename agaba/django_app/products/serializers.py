from django.db import models
from rest_framework import serializers
from .models import (
    Product, PriceHistory, Category, Subcategory,
    Attribute, ProductAttribute, ProductDocument,
    ProductPhoto, Dimensions, AdditionalOption,
    Question, Answer, Comparison, ProductReview,
    Favorite
)
from api.utils import upload_to_minio, delete_from_minio

from api.permissions import ReadOnly


class PriceHistorySerializer(serializers.ModelSerializer):
    permission_class = [ReadOnly]

    class Meta:
        model = PriceHistory
        fields = ['id', 'price', 'changed_at']


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute_id = serializers.PrimaryKeyRelatedField(
        source='attribute',
        queryset=Attribute.objects.all(),
        write_only=True
    )
    attribute_name = serializers.CharField(
        source='attribute.name',
        read_only=True
    )

    class Meta:
        model = ProductAttribute
        fields = ['id', 'attribute_id', 'attribute_name', 'value']

    def validate_attribute_id(self, value):
        """
        Проверка, что атрибут существует.
        """
        if not Attribute.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(
                "Атрибут с таким ID не существует."
            )
        return value

    def to_representation(self, instance):
        """
        Кастомное представление данных при чтении.
        Заменяем attribute_id на attribute с названием.
        """
        representation = super().to_representation(instance)
        representation.pop('attribute_id', None)
        representation['attribute'] = representation.pop('attribute_name')
        return representation

    def to_internal_value(self, data):
        """
        Кастомная обработка данных при записи.
        Позволяет использовать как 'attribute',
        так и 'attribute_id' при создании/обновлении.
        """
        if 'attribute' in data and 'attribute_id' not in data:
            data['attribute_id'] = data.pop('attribute')
        return super().to_internal_value(data)


class ProductDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDocument
        fields = ['id', 'document_url', 'description']


class ProductPhotoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = ProductPhoto
        fields = ['id', 'image', 'position', 'url']
        read_only_fields = ['url']

    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return obj.image.url if obj.image else None

    def create(self, validated_data):
        """
        Создает объект ProductPhoto.
        Если изображение передано, загружает его на MinIO.
        """
        image = validated_data.pop('image', None)
        if image:
            file_name = f"product_photos/{image.name}"
            minio_url = upload_to_minio(image, file_name)

            if not minio_url:
                raise serializers.ValidationError(
                    "Ошибка при загрузке файла на MinIO."
                )

            validated_data['image'] = minio_url
        else:
            validated_data['image'] = None

        return super().create(validated_data)

    def destroy(self, instance):
        """
        Удаляет объект ProductPhoto и соответствующий файл с MinIO.
        """
        file_url = instance.image.url if instance.image else None
        if file_url:
            file_name = file_url.split('/')[-1]
            delete_success = delete_from_minio(file_name)
            if not delete_success:
                raise serializers.ValidationError(
                    "Ошибка при удалении файла с MinIO."
                )

        instance.delete()


class ProductShortSerializer(serializers.ModelSerializer):
    short_description = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    prev_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'brand', 'name', 'short_description', 'cur_price', 'prev_price',
            'availability', 'rating'
        ]

    def get_short_description(self, obj):
        """
        Возвращает первые 50 символов описания товара.
        Если описание длиннее, добавляет многоточие.
        """
        if obj.description:
            return (
                obj.description[:50] + '...'
            ) if len(
                obj.description
            ) > 50 else obj.description
        return None

    def get_prev_price(self, obj):
        """
        Возвращает prev_price, только если она меньше cur_price.
        """
        if obj.prev_price and obj.prev_price < obj.cur_price:
            return obj.prev_price
        return None

    def get_rating(self, obj):
        """
        Возвращает средний рейтинг товара на основе отзывов.
        """
        reviews = obj.product_reviews.filter(status='approved')
        if reviews.exists():
            return round(
                reviews.aggregate(
                    avg_rating=models.Avg(
                        'rating'
                    )
                )['avg_rating'], 1
            )
        return None


class DimensionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dimensions
        fields = ['length', 'width', 'height', 'weight']


class AdditionalOptionSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = AdditionalOption
        fields = ['id', 'name', 'price']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug',
            'parent', 'image', 'is_terminal'
        ]


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = [
            'id', 'name', 'slug',
            'category', 'image', 'is_terminal'
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'user', 'rating', 'comment', 'pros', 'cons',
            'created_at', 'image', 'status', 'order'
        ]
        read_only_fields = ['user', 'created_at']

    def validate(self, data):
        # Проверяем, что рейтинг находится в допустимом диапазоне
        rating = data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return data


class ProductSerializer(serializers.ModelSerializer):
    cur_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    prev_price = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    price_history = PriceHistorySerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, required=False)
    documents = ProductDocumentSerializer(many=True, required=False)
    photos = ProductPhotoSerializer(many=True, required=False)
    dimensions = DimensionsSerializer(required=False)
    additional_options = AdditionalOptionSerializer(many=True, required=False)
    company_name = serializers.CharField(source='company.name', read_only=True)
    product_reviews = ProductReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'brand', 'name', 'slug', 'description', 'cur_price',
            'prev_price', 'category', 'subcategory',  'rating',
            'product_reviews', 'company', 'company_name', 'condition',
            'delivery_time',
            'availability', 'location', 'min_deposit', 'video_url', 'status',
            'created_at', 'updated_at', 'price_history', 'attributes',
            'documents', 'photos', 'dimensions', 'additional_options',
            'author',
        ]
        read_only_fields = [
            'id', 'created_at',
            'prev_price', 'rating',
            'updated_at', 'price_history'
        ]

    def create(self, validated_data):
        """
        Создает товар и связанные объекты (атрибуты, документы, фото и т.д.).
        """
        attributes_data = validated_data.pop('attributes', [])
        documents_data = validated_data.pop('documents', [])
        photos_data = validated_data.pop('photos', [])
        dimensions_data = validated_data.pop('dimensions', None)
        additional_options_data = validated_data.pop('additional_options', [])

        product = Product.objects.create(**validated_data) # Создаем основной объект товара

        for attribute_data in attributes_data:
            ProductAttribute.objects.create(product=product, **attribute_data) # Создаем атрибуты

        for document_data in documents_data:
            ProductDocument.objects.create(product=product, **document_data) # Создаем документы

        for photo_data in photos_data:
            ProductPhoto.objects.create(product=product, **photo_data) # Создаем фото

        if dimensions_data:
            Dimensions.objects.create(product=product, **dimensions_data) # Создаем габариты

        for option_data in additional_options_data:
            AdditionalOption.objects.create(product=product, **option_data) # Создаем доп. опции

        return product

    def get_prev_price(self, obj):
        """
        Возвращает предыдущую цену, только если она меньше текщей.
        """
        if obj.prev_price and obj.prev_price < obj.cur_price:
            return obj.prev_price
        return None

    def get_rating(self, obj):
        """
        Возвращает средний рейтинг товара на основе отзывов.
        """
        reviews = obj.product_reviews.filter(status='approved')
        if reviews.exists():
            return round(
                reviews.aggregate(
                    avg_rating=models.Avg(
                        'rating'
                    )
                )['avg_rating'], 1
            )
        return None


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'username', 'text', 'date', 'product']


# class AnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Answer
#         fields = ['id', 'user', 'question', 'text', 'date', 'product']


class ComparisonSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        many=True
    )
    session_key = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Comparison
        fields = ['id', 'products', 'user', 'session_key', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']

    def validate_products(self, products):
        """
        Проверяет, что продукты не дублируются в сравнении.
        """
        if len(products) != len(set(products)):
            raise serializers.ValidationError(
                "Продукты не должны дублироваться в сравнении."
            )
        return products


    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None
        session_key = attrs.get('session_key')

        if not session_key and request:
            session_key = (
                request.query_params.get('session_key')
                or request.headers.get('X-Session-Key')
                or getattr(request.session, 'session_key', None)
            )

        if not (user and user.is_authenticated) and not session_key:
            raise serializers.ValidationError(
                "session_key is required for anonymous comparisons."
            )

        attrs['session_key'] = session_key
        return attrs

    def create(self, validated_data):
        """
        Создает или обновляет сравнение для пользователя.
        """
        request = self.context.get('request')
        user = request.user if request else None
        products = validated_data.pop('products')
        session_key = validated_data.pop('session_key', None)

        if user and user.is_authenticated:
            comparison, created = Comparison.objects.get_or_create(
                user=user,
                defaults={'session_key': session_key, **validated_data}
            )
        else:
            comparison, created = Comparison.objects.get_or_create(
                session_key=session_key,
                defaults=validated_data
            )

        comparison.products.set(products)
        return comparison


class ProductComparisonSerializer(serializers.ModelSerializer):
    first_photo = serializers.SerializerMethodField()
    characteristics = serializers.SerializerMethodField()
    prev_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'first_photo',
            'brand',
            'name',
            'cur_price',
            'prev_price',
            'subcategory',
            'year_of_release',
            'availability',
            'characteristics'
        ]

    def get_first_photo(self, obj):
        """Получает 'главное'(фото спереди) фото товара."""
        first_photo = obj.photos.filter(position='front').first()
        return first_photo.image.url if first_photo else None

    def get_characteristics(self, obj):
        """Получает характеристики товара из модели ProductAttribute."""
        characteristics = {}
        for attr in obj.attributes.all():
            characteristics[attr.attribute.name] = attr.value
        return characteristics

    def get_prev_price(self, obj):
        """
        Возвращает старую цену товара, только
        если она меньше текущей цены и существует.
        """
        if obj.prev_price and obj.prev_price < obj.cur_price:
            return obj.prev_price
        return None


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""
    product = ProductShortSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'product', 'product_id', 'created_at']
        read_only_fields = ['created_at']

# Пример JSON добавления товара
# {
#   "brand": "Toyota",
#   "name": "Corolla",
#   "slug": "toyota-corolla-2023",
#   "description": "Надежный автомобиль для повседневного использования.",
#   "price": "250000",
#   "year_of_release": "2018",
#   "category": "1",
#   "subcategory": "1",
#   "author": "1",
#   "company": "1",
#   "condition": "new",
#   "delivery_time": "7",
#   "availability": "in_stock",
#   "location": "Moscow",
#   "min_deposit": "5000",
#   "video_url": "https://example.com/video.mp4",
#   "status": "active",
#   "attributes": [
#     {
#       "attribute": "1",
#       "value": "1.6L"
#     },
#     {
#       "attribute": "2",
#       "value": "Да"
#     }
#   ],
#   "documents": [
#     {
#       "document_url": "https://example.com/document.pdf",
#       "description": "Инструкция по эксплуатации"
#     }
#   ],
#   "photos": [
#     {
#       "position": "front"
#     },
#     {
#       "position": "back"
#     }
#   ],
#   "dimensions": {
#     "length": "4.5",
#     "width": "1.8",
#     "height": "1.5",
#     "weight": "1200"
#   },
#   "additional_options": [
#     {
#       "name": "Коврики в подарок",
#       "price": "0"
#     },
#     {
#       "name": "Тонировка",
#       "price": "10000"
#     }
#   ]
# }
