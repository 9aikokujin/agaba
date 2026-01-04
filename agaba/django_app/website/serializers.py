# # serializers.py
# from datetime import datetime

# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import serializers

# from api.utils import upload_to_minio

# from website.models import (
#     Category, Product, Price, UnitOfMeasurement,
#     AttributeGroup, AttributeTemplate, Attribute,
#     ProductImage, ProductDocument, AdditionalOption,
#     Question, Answer, Comparison, ProductReview, Favorite
# )
# # serializers.py
# from .models import Product, ProductImage, Attribute, AdditionalOption


# class PriceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Price
#         fields = ['id', 'price', 'date']
#         read_only_fields = ['date']


# class UnitOfMeasurementSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UnitOfMeasurement
#         fields = ['id', 'name', 'abbr']


# class AttributeTemplateSerializer(serializers.ModelSerializer):
#     meas_unit = UnitOfMeasurementSerializer(read_only=True)

#     class Meta:
#         model = AttributeTemplate
#         fields = [
#             'id', 'type', 'name', 'desc',
#             'meas_unit', 'placeholder', 'json_data',
#             'required'
#         ]


# class AttributeValueSerializer(serializers.ModelSerializer):
#     template = serializers.PrimaryKeyRelatedField(read_only=True)
#     value = serializers.CharField(allow_blank=True, allow_null=True)

#     class Meta:
#         model = Attribute
#         fields = ['id', 'template', 'value']

#     def validate(self, data):
#         """
#         Проверяем, что шаблон принадлежит категории товара.
#         """
#         product = self.context.get('product')
#         if not product:
#             raise serializers.ValidationError("Product is required in context.")

#         template = self.instance.template if self.instance else None
#         if not template:
#             raise serializers.ValidationError("Template is required.")

#         # Проверяем, что шаблон принадлежит категории товара
#         if template.group.category != product.category:
#             raise serializers.ValidationError("Template does not belong to the product's category.")
#         return data


# class ProductImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImage
#         fields = ['id', 'image', 'aspect']

#     def create(self, validated_data):
#         """
#         Переопределяем метод create для загрузки изображения на MinIO.
#         """
#         image_file = validated_data.pop('image')
#         aspect = validated_data.get('aspect')

#         # Генерируем уникальное имя файла
#         file_name = f"product_images/{image_file.name}"

#         # Загружаем файл на MinIO
#         file_url = upload_to_minio(image_file, file_name)
#         if not file_url:
#             raise serializers.ValidationError("Ошибка при загрузке изображения на MinIO.")

#         # Создаем запись в базе данных с URL изображения
#         return ProductImage.objects.create(image=file_url, aspect=aspect)


# class ProductDocumentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductDocument
#         fields = ['id', 'doc', 'name']


# class AdditionalOptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdditionalOption
#         fields = ['id', 'name', 'price']


# class ProductSerializer(serializers.ModelSerializer):
#     prices = PriceSerializer(many=True, read_only=True)
#     attributes = serializers.SerializerMethodField()
#     product_images = ProductImageSerializer(many=True, read_only=True)
#     product_docs = ProductDocumentSerializer(many=True, read_only=True)
#     additional_options = AdditionalOptionSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = [
#             'id', 'brand', 'name', 'slug', 'description', 'author',
#             'selling_company', 'created', 'updated', 'category',
#             'prod_year', 'condition', 'delivery_time_days',
#             'in_stock', 'location', 'min_down_payment_percentage',
#             'mod_status', 'video_link', 'attributes',
#             'length', 'width', 'height', 'weight',
#             'prices', 'product_images', 'product_docs', 'additional_options'
#         ]
#         read_only_fields = ['slug', 'created', 'updated']

#     def get_attributes(self, obj):
#         """
#         Возвращает список атрибутов для товара.
#         """
#         attributes = obj.attributes.all()
#         return AttributeValueSerializer(attributes, many=True).data

#     def validate(self, data):
#         """
#         Дополнительная валидация данных.
#         """
#         # Проверка года производства
#         if data.get('prod_year') and data['prod_year'] > datetime.now().year:
#             raise serializers.ValidationError(
#                 "Год производства не может быть больше текущего года."
#             )

#         # Проверка обязательных полей
#         required_fields = ['length', 'width', 'height', 'weight']
#         for field in required_fields:
#             if field not in data or data[field] is None:
#                 raise serializers.ValidationError(f"{field} is required.")

#         return data


# @api_view(['GET'])
# def get_attribute_templates(request, category_id):
#     """
#     Возвращает список шаблонов атрибутов для указанной категории.
#     """
#     templates = AttributeTemplate.objects.filter(
#         group__category_id=category_id
#     )
#     serializer = AttributeTemplateSerializer(templates, many=True)
#     return Response(serializer.data)
