# from .models import Product, ProductImage, ProductDocument


# def clone_product(product, idx):
#     """Клонировать существующий объект Product и сохранить его в базе данных."""
#     # Создаем копию объекта Product
#     product_copy = Product.objects.get(id=product.id)
#     product_copy.pk = None  # Установка pk в None создаст новый экземпляр
#     product_copy.link = None  # Установка pk в None создаст новый экземпляр
#     product_copy.name = f"Test_{idx}"  # Установка pk в None создаст новый экземпляр
#     product_copy.save()

#     # Копируем связи ManyToMany
#     for charact_item in product.charact_list.all():
#         product_copy.charact_list.add(charact_item)

#     for additional_option in product.additional_options.all():
#         product_copy.additional_options.add(additional_option)

#     # Сохраняем изменения
#     product_copy.save()

#     # Копируем связанные модели ProductImage
#     for image in product.product_images.all():
#         image_copy = ProductImage.objects.get(id=image.id)
#         image_copy.pk = None
#         image_copy.product = product_copy
#         image_copy.save()

#     # Копируем связанные модели ProductDocument
#     for doc in product.product_docs.all():
#         doc_copy = ProductDocument.objects.get(id=doc.id)
#         doc_copy.pk = None
#         doc_copy.product = product_copy
#         doc_copy.save()

#     return product_copy


# def clone_product_100_times():
#     # Получите первый объект Product из базы данных
#     original_product = Product.objects.get(link='trakhtor-volvo-t1000')

#     if original_product:
#         for idx in range(100):
#             clone_product(original_product, idx)