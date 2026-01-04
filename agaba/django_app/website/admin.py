# from django.contrib import admin
# from .models import (Product, ProductImage, ProductDocument,
#                      UnitOfMeasurement, AttributeGroup, AttributeTemplate,
#                      Attribute, Category,
#                      AdditionalOption, 
#                      ProductReview, Question)
# from django.utils.html import format_html
# from django import forms
# from django.templatetags.static import static
# from django.utils.safestring import mark_safe
# from django.forms.widgets import ClearableFileInput
# from django.urls import reverse
# from order.models import Order


# class AttributeGroupInline(admin.TabularInline):
#     model = AttributeGroup
#     extra = 1
#     fields = ('edit', 'name', 'attribute_templates_list')
#     readonly_fields = ('edit', 'attribute_templates_list')

#     def edit(self, obj):
#         if obj.id:
#             url = reverse('admin:website_attributegroup_change', args=[obj.id])
#             return format_html('<a href="{}"><strong>Edit</strong></a>', url)
#         else:
#             return ""
#     edit.short_description = ''

#     def attribute_templates_list(self, obj):
#         # Fetch all related AttributeTemplate instances
#         templates = obj.templates.all()
#         if templates:
#             # Create a list of links to the admin change page for each template
#             template_links = []
#             for template in templates:
#                 url = reverse('admin:website_attributetemplate_change', args=[template.id])
#                 template_links.append(format_html('<a href="{}">{}</a>', url, template.name))
#             return format_html(', '.join(template_links))
#         else:
#             return "No templates"
#     attribute_templates_list.short_description = 'Attribute Templates'


# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug', 'parent', 'image_tag', 'is_terminal')
#     fields = (
#         'name', 'slug', 'parent', 'image', 'image_tag',
#         'svg_icon', 'svg_icon_tag', 'is_terminal')
#     readonly_fields = ('image_tag', 'svg_icon_tag',)
#     inlines = [AttributeGroupInline]

#     # def formfield_for_dbfield(self, db_field, **kwargs):
#     #     if db_field.name == 'image':  # Replace with your image field name
#     #         kwargs['widget'] = ImagePreviewWidget
#     #     return super().formfield_for_dbfield(db_field, **kwargs)

#     # можно выбрать только не терминальные категории (на которые ссылаются другие категории)
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         # Customize the form field for the 'parent' ForeignKey
#         if db_field.name == 'parent':
#             # Filter the queryset for the 'parent' field
#             kwargs['queryset'] = Category.objects.filter(is_terminal=False)  # Only show non-terminal categories
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

#     def image_tag(self, obj):
#         obj_image = obj.image
#         if obj_image:
#             obj_image = obj_image.url
#         else:
#             obj_image = static('website/img/no_image.png')

#         return format_html(
#             '<img src="{}" width="auto" height="150" />', obj_image)
#     image_tag.short_description = 'Изображение'

#     def svg_icon_tag(self, obj):
#         return format_html(obj.svg_icon)
#     svg_icon_tag.short_description = 'SVG Иконка'

# # @admin.register(CharactItem)
# # class CharactItemAdmin(admin.ModelAdmin):
# #     autocomplete_fields = ['name']


# # @admin.register(Order)
# # class OrderAdmin(admin.ModelAdmin):
# #     list_display = ('user_id', 'product', 'stage', 'date_created')

# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     pass


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1  # Allow up to 10 images to be added
#     readonly_fields = ('image_tag',)
#     verbose_name = 'Изображение товара'
#     verbose_name_plural = 'Изображения товара'

#     def save_model(self, request, obj, form, change):
#         obj.save(request=request,
#                  use_existing=form.cleaned_data['use_existing'])

#     def image_tag(self, obj):
#         obj_image = obj.image
#         if obj_image:
#             obj_image = obj_image.url
#         else:
#             obj_image = static('website/img/no_image.png')

#         return format_html(
#             '<img src="{}" width="auto" height="150" />', obj_image)
#     image_tag.short_description = 'Image'


# class ProductDocumentInline(admin.TabularInline):
#     model = ProductDocument
#     extra = 1  # Allow up to 10 images to be added
#     fields = ('doc', 'name',)
#     verbose_name = "Документ о товаре"
#     verbose_name_plural = "Документы о товаре"

#     def save_model(self, request, obj, form, change):
#         obj.save(request=request,
#                  use_existing=form.cleaned_data['use_existing'])


# # class CharactItemInline(admin.TabularInline):
# #     model = CharactItem
# #     extra = 1  # Allow up to 30 characteristics to be added
# #     verbose_name = 'Характеристика'
# #     verbose_name_plural = 'Характеристики'


# # class AdditionalOptionInline(admin.TabularInline):
# #     model = AdditionalOption
# #     extra = 1  # Allow up to 30 characteristics to be added
# #     verbose_name = 'Дополнительная опция'
# #     verbose_name_plural = 'Дополнительные опции'


# class AttributeInline(admin.TabularInline):
#     model = Attribute
#     verbose_name = 'Характеристики товара'
#     verbose_name_plural = 'Характеристика товара'


# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = '__all__'
#         widgets = {
#             'min_down_payment_percentage': forms.NumberInput(attrs={'min': 0, 'max': 100}),  # Add HTML5 validation
#         }


# # @admin.register(AdditionalOption)
# # class AdditionalOptionAdmin(admin.ModelAdmin):
# #     autocomplete_fields = ['name']


# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     form = ProductForm
#     # inlines = [ProductImageInline, AttributeInline, AdditionalOptionInline, ProductDocumentInline]
#     inlines = [ProductImageInline, AttributeInline, ProductDocumentInline]
#     # Exclude the ManyToMany fields from the main form
#     exclude = ('charact_list', 'additional_options', 'slug', 'author')
#     readonly_fields = ('slug', )
#     list_display = (
#         'name', 'brand', 'category', 'image_tag', 'slug', 'author', 'created', 'in_stock')

#     # list_filter = ('in_stock',)

#     # Define the custom admin action
#     # actions = ['make_in_stock']

#     # def save_model(self, request, obj, form, change):
#     #     obj.author = request.user

#     #     super().save_model(request, obj, form, change)

#     def image_tag(self, obj):

#         obj_image = obj.product_images.first()
#         if obj_image:
#             obj_image = obj_image.image.url
#         else:
#             obj_image = static('website/img/no_image.png')

#         return format_html(
#             '<img src="{}" width="auto" height="150" />', obj_image)

#     image_tag.short_description = 'ГЛАВНОЕ ИЗОБРАЖЕНИЕ'

#     # можно выбрать только терминальные категории (в которые можно добавлять товары)
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == 'category':
#             kwargs['queryset'] = Category.objects.filter(is_terminal=True)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

#     # Custom action to set in_stock = True for selected products
#     # def make_in_stock(self, request, queryset):
#     #     updated_count = queryset.update(in_stock=True)
#     #     self.message_user(request, f'{updated_count} products were marked as in stock.')

#     # make_in_stock.short_description = "Mark selected products as in stock"

# # @admin.register(ProductImage)
# # class ProductImageAdmin(admin.ModelAdmin):
# #     list_display = ('image', )
# #     readonly_fields = ('image_hash',)


# # @admin.register(ProductDocument)
# # class ProductDocumentAdmin(admin.ModelAdmin):
# #     list_display = ('doc', 'name', )
# #     readonly_fields = ('doc_hash',)


# # @admin.register(CharactItem)
# # class CharactItemAdmin(admin.ModelAdmin):
# #     pass


# # @admin.register(AdditionalOption)
# # class AdditionalOptionAdmin(admin.ModelAdmin):
# #     pass

# # @admin.register(AdditionalOptionName)
# # class AdditionalOptionNameAdmin(admin.ModelAdmin):
# #     search_fields = ['name']

# #     # not show in nav bar
# #     def get_model_perms(self, request):
# #         return {}


# # @admin.register(CharactItemName)
# # class CharactItemNameAdmin(admin.ModelAdmin):
# #     search_fields = ['name']

# #     # not show in nav bar
# #     def get_model_perms(self, request):
# #         return {}

# # @admin.register(Order)
# # class OrderAdmin(admin.ModelAdmin):
# #     list_display = ('buyer_id', 'product', 'stage', 'date_created')

# # @admin.register(Question)
# # class QuestionAdmin(admin.ModelAdmin):
# #     pass


# class ImagePreviewWidget(ClearableFileInput):
#     def render(self, name, value, attrs=None, renderer=None):
#         output = super().render(name, value, attrs, renderer)
#         print(output)
#         if value and hasattr(value, "url"):
#             output = mark_safe(
#                 f'{output}<img src="{value.url}" style="max-height: 150px; max-width: 150px; margin-bottom: 10px;" />'
#             )
#         return output


# @admin.register(UnitOfMeasurement)
# class UnitOfMeasurementAdmin(admin.ModelAdmin):
#     list_display = ('name', 'abbr')
#     # search_fields = ('name', 'abbr')
#     # list_filter = ('name',)
#     ordering = ('id',)


# class AttributeTemplateInline(admin.TabularInline):
#     model = AttributeTemplate
#     extra = 1
#     fields = ('edit', 'name', 'desc', 'type', 'meas_unit', 'required', 'placeholder')
#     readonly_fields = ('edit', )
#     verbose_name = "Шаблон атрибута"
#     verbose_name_plural = "Шаблоны атрибутов"

#     def edit(self, obj):
#         if obj.id:
#             url = reverse('admin:website_attributetemplate_change', args=[obj.id])
#             return format_html('<a href="{}"><strong>Edit</strong></a>', url)
#         else:
#             return ""
#     edit.short_description = ''


# @admin.register(AttributeGroup)
# class AttributeGroupAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category')
#     # search_fields = ('name', 'category__name')
#     # list_filter = ('category',)
#     ordering = ('name',)
#     inlines = [AttributeTemplateInline]

#     # можно выбрать только терминальные категории (в которые можно добавлять товары)
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == 'category':
#             kwargs['queryset'] = Category.objects.filter(is_terminal=True)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
#     def has_module_permission(self, request):
#         # Return False to hide the model from the admin index page
#         return False


# @admin.register(AttributeTemplate)
# class AttributeTemplateAdmin(admin.ModelAdmin):
#     list_display = ('name', 'type', 'group', 'meas_unit', 'required')
#     search_fields = ('name', 'type', 'group__name', 'meas_unit__name')
#     list_filter = ('type', 'group', 'required')
#     ordering = ('name',)

#     def has_module_permission(self, request):
#         # Return False to hide the model from the admin index page
#         return False

# @admin.register(Attribute)
# class AttributeAdmin(admin.ModelAdmin):
#     list_display = ('template', 'product', 'value')
#     search_fields = ('template__name', 'product__name', 'value')
#     list_filter = ('template', 'product')
#     ordering = ('template__name',)

#     def has_module_permission(self, request):
#         # Return False to hide the model from the admin index page
#         return False