# ПЕРЕХОД НА DRF
# import base64
# from django.db import transaction
# import json
# import re
# from decimal import Decimal
# from django.contrib import messages
# from django.contrib.auth import login, logout
# from django.contrib.auth.decorators import login_required
# from django.core.files.base import ContentFile
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.urls import reverse
# from django.views.decorators.csrf import csrf_protect
# from django.views.decorators.http import require_http_methods
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# from .forms import UpdateInformations, CompanyForm
# from .models import CustomUser, Company

# from balance.models import Balance, AllOperation

# from website.forms import ReviewForm
# from balance.forms import ReplenishmentForm, WithdrawalForm
# from website.models import (
#     AdditionalOption,
#     Comparison,
#     Favorite,
#     Category,
#     Attribute,
#     AttributeTemplate,
#     Product,
#     Price,
#     ProductImage,
#     ProductReview,
#     Question,
#     Category,
# )
# from order.models import Order, DeliveryOrder
# from messenger.models import Message

# # Тест логирования
# import logging

# # Создаем логгер для вашего приложения
# logger = logging.getLogger(__name__)


# NUMBER_DIGITS_OTP = 6

# IMAGE_PLACEHOLDERS = [
#     {"id": "uploadFront", "src": "front.png",
#         "alt": "front side car image", "label": "спереди"},
#     {"id": "uploadBack", "src": "back.png",
#         "alt": "back side car image", "label": "сзади"},
#     {"id": "uploadLeft", "src": "left.png",
#         "alt": "left side car image", "label": "слева"},
#     {"id": "uploadRight", "src": "right.png",
#         "alt": "right side car image", "label": "справа"},
#     {"id": "uploadFrontLeft", "src": "front_left.png",
#         "alt": "front left side car image", "label": "спереди левый угол"},
#     {"id": "uploadFrontRight", "src": "front_right.png",
#         "alt": "front right side car image", "label": "спереди правый угол"},
#     {"id": "uploadBackLeft", "src": "back_left.png",
#         "alt": "back left side car image", "label": "сзади левый угол"},
#     {"id": "uploadBackRight", "src": "back_right.png",
#         "alt": "back right side car image", "label": "сзади правый угол"}
# ]


# @csrf_protect
# def auth_user(request):
#     # Если пользователь уже аутентифицирован,
#     # перенаправляем на главную страницу
#     if request.user.is_authenticated:
#         return redirect(reverse('home'))

#     if request.method == 'POST':
#         # Получаем данные из POST-запроса
#         user_type = request.POST.get('user_type', '').strip()
#         username = request.POST.get('mobile_number', '').strip()

#         # Проверка наличия обязательных полей
#         if not username:
#             messages.error(request, 'Номер телефона не указан!')
#             return JsonResponse(
#                 {'status': 'failed',
#                  'error': 'Номер телефона не указан.'}
#             )
#         if not user_type:
#             messages.error(request, 'Тип пользователя не указан!')
#             return JsonResponse(
#                 {'status': 'failed',
#                  'error': 'Тип пользователя не указан.'}
#             )

#         # Проверка формата номера телефона
#         phone_pattern = r'^\+?\d{10,15}$'
#         if not re.match(phone_pattern, username):
#             messages.error(request, 'Неверный формат номера телефона.')
#             return JsonResponse(
#                 {'status': 'failed',
#                  'error': 'Неверный формат номера телефона.'}
#             )

#         try:
#             # Проверяем, существует ли пользователь с таким номером телефона
#             user = CustomUser.objects.get(username=username)
#             if user_type == 'seller' and user.role == 'buyer':
#                 messages.error(
#                     request,
#                     'Покупатель с таким номером телефона уже существует!'
#                 )
#                 return JsonResponse(
#                     {'status': 'failed',
#                      'error': 'Пользователь уже зарегистрирован.'}
#                 )
#         except CustomUser.DoesNotExist:
#             # Создаем нового пользователя
#             try:
#                 user = CustomUser.objects.create_user(
#                     username=username,
#                     role=user_type,
#                     is_active=False
#                 )

#                 # Если пользователь — продавец, создаем связанную компанию
#                 if user_type == 'seller':
#                     company_name = request.POST.get('company_name', '').strip()
#                     company_inn = request.POST.get('company_inn', '').strip()

#                     if not company_name or not company_inn:
#                         messages.error(request, 'Данные компании не указаны!')
#                         return JsonResponse(
#                             {'status': 'failed',
#                              'error': 'Данные компании не указаны.'}
#                         )

#                     Company.objects.create(
#                         user=user, inn=company_inn,
#                         name=company_name
#                     )

#             except Exception as e:
#                 # Логируем ошибку создания пользователя
#                 messages.error(
#                     request,
#                     f'Ошибка при создании пользователя: {str(e)}'
#                 )
#                 return JsonResponse(
#                     {'status': 'failed',
#                      'error': 'Ошибка при создании пользователя.'}
#                 )

#         # Генерация OTP
#         otp = user.generate_otp()
#         print(f"Generated OTP: {otp}")  # Уберите эту строку в продакшене!

#         # Сохранение данных в сессии
#         request.session['user_id'] = user.id

#         # Возвращаем успешный ответ
#         return JsonResponse({
#             'status': 'success',
#             'message': 'OTP отправлен.',
#             'received_mobile_otp': otp  # Только для тестирования!
#         })

#     # Если запрос не POST, рендерим форму
#     return render(request, 'account/authentication.html')


# @csrf_protect
# def auth_user_verify_otp(request):
#     """Проверка OTP для аутентификации пользователя."""
#     user_id = request.session.get('user_id')
#     user = get_object_or_404(CustomUser, id=user_id)

#     if request.method == 'POST':
#         # Предполагается 6-значный OTP
#         entered_otp = ''.join(
#             request.POST[f'digit_{i}'] for i in range(5)
#         )

#         # Проверка OTP
#         if user.verify_otp(entered_otp):
#             user.is_active = True
#             user.save()
#             login(request, user)

#             # Проверка редиректа
#             redirect_url = request.session.pop('next', None)
#             if redirect_url:
#                 return JsonResponse(
#                     {'status': 'success',
#                      'redirect_url': redirect_url}
#                 )

#             return JsonResponse(
#                 {'status': 'success',
#                  'redirect_url': reverse('home')}
#             )

#         return JsonResponse(
#             {'status': 'failed',
#              'error': 'Неверный или просроченный OTP'}
#         )

#     return JsonResponse({'status': 'failed', 'error': 'Неверный запрос'})


# def auth_seller(request):
#     return render(request, 'account/auth_seller.html')


# @login_required
# def home(request):
#     """Главная страница личного кабинета."""
#     # select_related для OneToOneField - один JOIN запрос
#     try:
#         balance = Balance.objects.select_related('user').get(user=request.user)
#     except Balance.DoesNotExist:
#         balance = Balance.objects.create(user=request.user)
#     
#     # Для простого ForeignKey фильтра select_related не нужен, но можно использовать
#     companies = Company.objects.filter(user=request.user, is_hidden=False)
#     
#     # prefetch_related для Favorite -> Product и его связи (category, company, images)
#     # Это оптимизирует N+1 запросы при обращении к product.category, product.company и т.д.
#     favorite_products = Favorite.objects.filter(
#         user=request.user
#     ).select_related(
#         'product',  # ForeignKey - используем select_related
#         'product__category',  # ForeignKey через product
#         'product__subcategory',  # ForeignKey через product
#         'product__company',  # ForeignKey через product
#     ).prefetch_related(
#         'product__product_images',  # Reverse ForeignKey (ManyToOne) - prefetch_related
#         'product__favorites',  # Reverse ForeignKey - если нужно
#     )[:10]  # Ограничение количества
#     
#     # select_related для Order -> Product и его связи
#     # prefetch_related для ManyToMany и reverse ForeignKey
#     orders = Order.objects.filter(
#         user=request.user
#     ).select_related(
#         'product',  # ForeignKey
#         'product__category',  # ForeignKey через product
#         'product__company',  # ForeignKey через product
#         'company',  # ForeignKey напрямую
#     ).prefetch_related(
#         'selected_additional_options',  # ManyToMany - prefetch_related
#         'product__product_images',  # Reverse ForeignKey
#     ).order_by('-date_created')[:5]  # Ограничение количества
#     
#     view_id = 'home'
#     context = {
#         'browser_tab_name': "Личный кабинет",
#         'balance': balance,
#         'companies': companies,
#         'favorite_products': favorite_products,
#         'orders': orders,
#         'view_id': view_id,
#     }
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# @login_required
# def products(request):
#     """Товары продавца."""
#     # Базовый QuerySet с оптимизацией связей
#     products_all = Product.objects.filter(
#         author=request.user
#     ).select_related(
#         'category',  # ForeignKey
#         'subcategory',  # ForeignKey
#         'author',  # ForeignKey (хотя уже фильтруем по нему)
#         'company',  # ForeignKey
#     ).prefetch_related(
#         'product_images',  # Reverse ForeignKey (ProductImage)
#         'attributes',  # Reverse ForeignKey (Attribute)
#         'additional_options',  # Reverse ForeignKey (AdditionalOption)
#     ).order_by('-created_at')  # Правильное поле из модели
#     
#     # Группировка по статусам - правильные значения из STATUS_CHOICES
#     products = {
#         'active': products_all.filter(status='active'),
#         'on_moderation': products_all.filter(status='on_moderation'),
#         'rejected': products_all.filter(status='rejected'),
#         'removed': products_all.filter(status='removed'),
#     }
#     
#     view_id = 'products'
#     context = {
#         'browser_tab_name': "Товары",
#         'products': products,
#         'view_id': view_id,
#     }
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# @login_required
# def advertisement(request):
#     """Реклама продавца."""
#     view_id = 'advertisement'
#     context = {
#         'browser_tab_name': "Реклама",
#         'view_id': view_id,
#     }
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# @login_required
# def orders(request):
#     """Заказы пользователя."""
#     # select_related для ForeignKey связей
#     # prefetch_related для ManyToMany и reverse ForeignKey
#     orders = Order.objects.filter(
#         user=request.user
#     ).select_related(
#         'product',  # ForeignKey
#         'product__category',  # ForeignKey через product
#         'product__subcategory',  # ForeignKey через product
#         'product__company',  # ForeignKey через product
#         'company',  # ForeignKey напрямую
#         'user',  # ForeignKey (хотя уже фильтруем по нему)
#         'bank_for_leasing',  # ForeignKey (может быть null)
#     ).prefetch_related(
#         'selected_additional_options',  # ManyToMany
#         'product__product_images',  # Reverse ForeignKey через product
#         'deliveries',  # Reverse ForeignKey (DeliveryOrder)
#         'manager_assignment',  # Reverse OneToOneField
#         'manager_assignment__manager',  # ForeignKey через manager_assignment
#     ).order_by('-date_created')
#     
#     # select_related для DeliveryOrder
#     deliveries = DeliveryOrder.objects.filter(
#         user=request.user
#     ).select_related(
#         'product',  # ForeignKey
#         'product__category',  # ForeignKey через product
#         'product__company',  # ForeignKey через product
#         'company',  # ForeignKey
#         'user',  # ForeignKey
#         'order',  # ForeignKey
#         'order__product',  # ForeignKey через order
#         'dimensions',  # ForeignKey (может быть null)
#     ).prefetch_related(
#         'product__product_images',  # Reverse ForeignKey
#     ).order_by('-date_created')
#     
#     view_id = 'orders'
#     context = {
#         'browser_tab_name': "Заказы",
#         'orders': orders,
#         'deliveries': deliveries,
#         'view_id': view_id,
#     }
#     return render(
#         request,
#         f'account/nav_tabs/{view_id}.html',
#         context
#     )


# @login_required
# def favorites(request):
#     """Избранные товары пользователя."""
#     view_id = 'favorites'
#     context = {
#         'browser_tab_name': "Реклама",
#         'view_id': view_id,
#     }
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# @login_required
# def compare(request):
#     """Сравнение товаров пользователя."""
#     comparisons = Comparison.objects.filter(user=request.user)
#     products = [comparison.product for comparison in comparisons]

#     # Группируем товары по их группе
#     groups = {}
#     for product in products:
#         group_name = product.group.name  # Если group — это ForeignKey
#         groups[group_name] = groups.get(group_name, 0) + 1

#     view_id = 'compare'
#     context = {
#         'browser_tab_name': "Сравнить",
#         'products': products,
#         'groups': groups,  # Передаём группы и их количество
#         'view_id': view_id,
#     }
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# def profile(request):
#     """Редактирование профиля пользователя."""
#     # Инициализируем форму заранее
#     form = UpdateInformations(instance=request.user)
#     companies = Company.objects.filter(user=request.user)
#     view_id = 'profile'
#     if request.method == 'POST':
#         print(request.POST)
#         print("FILES Data:", request.FILES)
#         form = UpdateInformations(
#             request.POST, request.FILES,
#             instance=request.user
#         )
#         if form.is_valid():
#             form.save()
#             return redirect('profile')
#         else:
#             print(form.errors)

#     view_id = 'profile'
#     context = {
#         'form': form,
#         'browser_tab_name': "Профиль",
#         'companies': companies,
#         'view_id': view_id,
#     }
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# @login_required
# def notifications(request):
#     """Уведомления пользователя."""
#     # notifications = request.user.notifications.all()
#     view_id = 'notifications'
#     context = {
#         'browser_tab_name': "Уведомления",
#         'view_id': view_id,
#     }
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# @login_required
# def balance(request):
#     """Баланс пользователя."""
#     user_balance = Balance.objects.get(user=request.user)
#     all_operations = AllOperation.objects.filter(
#         user=request.user
#     ).order_by('-date_created')

#     # Фильтрация компаний: только компании пользователя, которые не скрыты
#     companies = Company.objects.filter(user=request.user, is_hidden=False)

#     # Инициализация форм
#     form_rep = ReplenishmentForm()
#     form_comp = CompanyForm()
#     form_wit = WithdrawalForm()

#     # Определение контекста заранее
#     context = {
#         'browser_tab_name': "Баланс",
#         'balance': "balance",
#         'user_balance': user_balance,
#         'form_rep': form_rep,
#         'form_wit': form_wit,
#         'companies': companies,
#         'form_comp_errors': None,  # Для отладки
#         'form_rep_errors': None,
#     }
#     if request.method == 'POST':
#         print("POST data:", request.POST)  # Отладочный вывод

#         if 'submit_replenishment' in request.POST:
#             form_rep = ReplenishmentForm(request.POST)

#             # Проверяем существование компании перед созданием формы
#             inn_from_post = request.POST.get('inn')  # Получаем ИНН из POST-запроса
#             user = request.user

#             try:
#                 # Проверяем, существует ли компания с указанным ИНН
#                 company = Company.objects.get(inn=inn_from_post, user=user)
#                 company_exists = True
#             except Company.DoesNotExist:
#                 company_exists = False

#             # Создаем форму CompanyForm только если компания не существует
#             if company_exists:
#                 form_comp = None  # Форма не нужна, так как компания уже существует
#             else:
#                 form_comp = CompanyForm(request.POST)

#             print("POST data:", request.POST)
#             print("ReplenishmentForm valid:", form_rep.is_valid())
#             if form_comp:
#                 print("CompanyForm valid:", form_comp.is_valid())

#             # Проверяем валидность форм
#             if form_rep.is_valid() and (form_comp is None or form_comp.is_valid()):
#                 if not company_exists:
#                     company_data = form_comp.cleaned_data

#                     # Инвертируем значение поля is_hidden
#                     is_hidden = request.POST.get("is_hidden") != "on"  # если чекбокс не отмечен, будет True (скрыто), если отмечен - False (видимо)
#                     print(f"is_hidden value: {is_hidden}")

#                     # Проверяем количество видимых компаний (is_hidden=False)
#                     visible_companies_count = Company.objects.filter(
#                         user=user, is_hidden=False
#                     ).count()
#                     if not is_hidden and visible_companies_count >= 5:
#                         messages.error(
#                             request,
#                             "Добавлено максимальное количество компаний."
#                             "Удалите одну из существующих."
#                         )
#                         return render(request, 'account/balance.html', context)

#                     # Создаем новую компанию
#                     company = Company.objects.create(
#                         inn=company_data['inn'],
#                         name=company_data['name'],
#                         kpp=company_data['kpp'],
#                         legal_address=company_data['legal_address'],
#                         ogrn=company_data['ogrn'],
#                         user=user,
#                         is_hidden=is_hidden
#                     )
#                     print(f"Компания добавлена: {company}")

#                 # Создание пополнения
#                 replenishment = form_rep.save(commit=False)
#                 replenishment.user = user
#                 replenishment.company = company
#                 replenishment.status_operation = 'pending'
#                 replenishment.payment_type = 'account'
#                 replenishment.save()

#                 messages.success(
#                     request,
#                     "Заявка на пополнение успешно создана."
#                 )
#             else:
#                 print("ReplenishmentForm errors:", form_rep.errors)
#                 if form_comp:
#                     print("CompanyForm errors:", form_comp.errors)
#                 messages.error(request, 'Исправьте ошибки в форме')

#         elif 'submit_withdrawal' in request.POST:
#             form_wit = WithdrawalForm(request.POST)
#             form_comp = CompanyForm(request.POST)

#             print("POST data:", request.POST)
#             print("WithdrawalForm valid:", form_wit.is_valid())
#             print("CompanyForm valid:", form_comp.is_valid())

#             if form_wit.is_valid() and form_comp.is_valid():
#                 user = request.user
#                 company_data = form_comp.cleaned_data

#                 # Создание/обновление компании
#                 company, created = Company.objects.update_or_create(
#                     inn=company_data['inn'],
#                     defaults={
#                         'name': company_data['name'],
#                         'kpp': company_data['kpp'],
#                         'legal_address': company_data['legal_address'],
#                         'ogrn': company_data['ogrn'],
#                         'user': user,
#                         'is_hidden': not company_data.get('is_hidden', False)
#                     }
#                 )

#                 # Создание пополнения
#                 withdrawal = form_wit.save(commit=False)
#                 withdrawal.user = user
#                 withdrawal.company = company
#                 withdrawal.status_operation = 'pending'
#                 withdrawal.payment_type = 'account'
#                 withdrawal.save()

#             else:
#                 print("WithdrawalForm errors:", form_wit.errors)
#                 print("CompanyForm errors:", form_comp.errors)

#     # Пагинация
#     paginator = Paginator(all_operations, 20)
#     page = request.GET.get('page', 1)
#     try:
#         operations = paginator.page(page)
#     except (EmptyPage, PageNotAnInteger):
#         operations = paginator.page(1)
#     view_id = 'balance'
#     # Обновляем контекст перед возвратом
#     context.update({
#         'operations': operations,
#         'form_comp_errors': form_comp.errors if form_comp else None,
#         'form_rep_errors': form_rep.errors,
#         'view_id': view_id,
#     })
#     # Надо думать что если дурачек сначала не нажал чекбокс,
#     # а потом захотел вдруг сохранить при следующем запросе,
#     # то привязываем компанию к пользователю!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# @login_required
# def reviews_view(request):
#     """Отзывы/вопросы пользователя."""
#     all_question = Question.objects.filter(username=request.user)

#     # Получаем продукты, которые были куплены пользователем
#     products = Product.objects.filter(orders__user=request.user)
    
#     # Исключаем продукты, по которым пользователь уже оставил отзыв
#     reviewed_products = ProductReview.objects.filter(user=request.user).values('product_id')
#     products = products.exclude(id__in=reviewed_products)

#     orders = Order.objects.filter(user=request.user, stage='Stage_4')
#     questions = all_question.filter(username=request.user)
#     reviews = ProductReview.objects.filter(user=request.user)

#     # Обработка формы
#     if request.method == "POST":
#         form = ReviewForm(request.POST, request.FILES)

#         if form.is_valid():
#             logger.debug("Форма прошла валидацию")

#             review = form.save(commit=False)
#             review.user = request.user

#             product_id = request.POST.get('product_id')
#             if product_id:
#                 try:
#                     product = get_object_or_404(Product, id=product_id)
#                     review.product = product
#                     review.save()
#                     return redirect('account', view_id='reviews')
#                 except Exception as e:
#                     logger.error(f"Ошибка при получении товара или сохранении отзыва: {e}")
#             else:
#                 form.add_error(None, "Товар не указан")
#         else:
#             logger.error(f"Форма невалидна: {form.errors}")
#     else:
#         form = ReviewForm()
#     view_id = 'reviews'
#     context = {
#         'browser_tab_name': "Отзывы и вопросы",
#         'questions': questions,
#         'reviews': reviews,
#         'products': products,
#         'orders': orders,
#         'form': form,
#         'view_id': view_id,
#     }
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# @login_required
# def help(request):
#     """Помощь пользователю."""
#     view_id = 'help'
#     context = {
#         'browser_tab_name': "Помощь",
#         'view_id': view_id
#     }
#     return render(request, f'account/nav_tabs/{view_id}.html', context)


# @login_required
# def logout_view(request):
#     """Выход из аккаунта."""
#     logout(request)
#     return redirect('/')
# # КОНЕЦ ЛИЧНОГО КАБИНЕТА ПОЛЬЗОВАТЕЛЯ


# # УПРАВЛЕНИЕ ТОВАРАМИ
# @login_required
# def add_new_product(request, category_slug=None,):
#     """Добавление нового товара."""

#     if request.method == 'POST':  # Шаг 2: ввод информации о товаре
#         try:
#             with transaction.atomic():
#                 category = get_object_or_404(Category, slug=category_slug)
#                 form_data = json.loads(request.body)
#                 attr_inputs = form_data['attrInputsData']
#                 print(attr_inputs)
#                 text_inputs = attr_inputs['textInputs']
#                 # Аккаунт продавца
#                 author = request.user
#                 # Компания, продающая товар.
#                 # Если у продавца несколько компаний, то выбираем первую
#                 # Это временное решение!!! Должен быть выбор компании в форме
#                 selling_company = Company.objects.filter(user=author).first()
#                 # Создаем товар
#                 product = Product.objects.create(
#                     author=author,
#                     selling_company=selling_company,
#                     category=category,
#                     brand=text_inputs.pop('brand'),
#                     name=text_inputs.pop('name'),
#                     description=text_inputs.pop('description'),
#                     prod_year=text_inputs.pop('prod_year'),
#                     delivery_time_days=text_inputs.pop('delivery_time_days'),
#                     location=text_inputs.pop('location'),
#                     min_down_payment_percentage=25,
#                     video_link=text_inputs.pop('video_link'),
#                 )

#                 # Создаем цену товара
#                 Price.objects.create(
#                     product=product,
#                     price=text_inputs.pop('price'),
#                 )

#                 # Создаем атрибуты (свойства) товара
#                 # Attr type TEXT
#                 for key, value in text_inputs.items():
#                     attribute_template = get_object_or_404(
#                         AttributeTemplate, id=key)
#                     Attribute.objects.create(
#                         template=attribute_template,
#                         product=product,
#                         value=value
#                     )
#                 # Attr type RADIO
#                 for key, value in attr_inputs['radioInputs'].items():
#                     attribute_template = get_object_or_404(
#                         AttributeTemplate, id=key)
#                     Attribute.objects.create(
#                         template=attribute_template,
#                         product=product,
#                         key=value[0],
#                         value=value[1],
#                     )
#                 # Attr type DROPDOWN
#                 for key, value in attr_inputs['dropdownInputs'].items():
#                     attribute_template = get_object_or_404(
#                         AttributeTemplate, id=key)
#                     Attribute.objects.create(
#                         template=attribute_template,
#                         product=product,
#                         key=value[0],
#                         value=value[1],
#                     )

#                 # Создаем изображения товара
#                 for aspect, image in form_data['imageInputsData'].items():

#                     # Decode the base64 image
#                     format, imgstr = image.split(';base64,')
#                     # Get the file extension (e.g., 'jpeg')
#                     ext = format.split('/')[-1]
#                     image_data = base64.b64decode(imgstr)

#                     # Create a ProductImage instance
#                     product_image = ProductImage(
#                         product=product, aspect=aspect)
#                     product_image.image.save(
#                         f'image.{ext}', ContentFile(image_data), save=True)

#                 # Создаем дополнительные опции товара
#                 for option, value in form_data['additionalOptionsData'].items():

#                     opt_name = AdditionalOptionName.objects.get_or_create(
#                         name=option)[0]

#                     AdditionalOption.objects.create(
#                         name=opt_name, product=product, price=value)

#                 return JsonResponse({'status': 'success',
#                                     'message': 'Товар создан'})

#         except Exception as e:
#             print(e)
#             return JsonResponse(
#                 {'status': 'error', 'message': 'Товар НЕ создан'})

#     else:  # Шаг 1: выбор категории товара
#         context = {
#             'browser_tab_name': "Публикация товара",
#             'image_placeholders': IMAGE_PLACEHOLDERS,
#         }

#         # категория товара выбрана
#         # если не выбрана откроется окно выбора
#         if category_slug:

#             category = get_object_or_404(Category, slug=category_slug)
#             context['category'] = category

#         return render(request, 'account/manage_products.html', context)


# @login_required
# def edit_product(request, slug):
#     """Редактирование товара продавцом"""

#     product = get_object_or_404(Product, slug=slug)

#     if request.method == 'POST':
#         try:
#             with transaction.atomic():
#                 form_data = json.loads(request.body)
#                 attr_inputs = form_data['attrInputsData']
#                 text_inputs = attr_inputs['textInputs']

#                 # Обновляем основные данные товара
#                 product.brand = text_inputs.pop('brand')
#                 product.name = text_inputs.pop('name')
#                 product.description = text_inputs.pop('description')
#                 product.prod_year = text_inputs.pop('prod_year')
#                 product.delivery_time_days = text_inputs.pop(
#                     'delivery_time_days')
#                 product.location = text_inputs.pop('location')
#                 product.video_link = text_inputs.pop('video_link')
#                 product.save()

#                 # Обновляем цену товара, если она изменилась
#                 # last_price = Price.objects.filter(product=product).order_by('-date').first()
#                 # print(type(product.cur_price))
#                 # print(type(text_inputs['price']))
#                 # print(product.cur_price != Decimal(text_inputs['price']))

#                 print(product.price_history)

#                 price = text_inputs.pop('price')
#                 if product.cur_price != Decimal(price):
#                     Price.objects.create(
#                         product=product,
#                         price=price,
#                     )

#                 # Обновляем атрибуты (свойства) товара
#                 # Attr type TEXT
#                 for key, value in text_inputs.items():
#                     attribute_template = get_object_or_404(
#                         AttributeTemplate, id=key)
#                     attribute, created = Attribute.objects.get_or_create(
#                         template=attribute_template,
#                         product=product,
#                         defaults={'value': value}
#                     )
#                     if not created:
#                         attribute.value = value
#                         attribute.save()

#                 # Attr type RADIO
#                 for key, value in attr_inputs['radioInputs'].items():
#                     attribute_template = get_object_or_404(
#                         AttributeTemplate, id=key)
#                     attribute, created = Attribute.objects.get_or_create(
#                         template=attribute_template,
#                         product=product,
#                         defaults={'key': value[0], 'value': value[1]}
#                     )
#                     if not created:
#                         attribute.key = value[0]
#                         attribute.value = value[1]
#                         attribute.save()

#                 # Attr type DROPDOWN
#                 for key, value in attr_inputs['dropdownInputs'].items():
#                     attribute_template = get_object_or_404(
#                         AttributeTemplate, id=key)
#                     attribute, created = Attribute.objects.get_or_create(
#                         template=attribute_template,
#                         product=product,
#                         defaults={'key': value[0], 'value': value[1]}
#                     )
#                     if not created:
#                         attribute.key = value[0]
#                         attribute.value = value[1]
#                         attribute.save()

#                 # Обновляем изображения товара
#                 # Удаляем старые изображения, если они были удалены на фронте
#                 existing_image_aspects = {img.aspect for img in product.product_images.all()}
#                 new_image_aspects = set(form_data['imageInputsData'].keys())
#                 images_to_delete = existing_image_aspects - new_image_aspects
#                 ProductImage.objects.filter(product=product, aspect__in=images_to_delete).delete()

#                 # Добавляем новые изображения
#                 for aspect, image in form_data['imageInputsData'].items():
#                     if aspect in existing_image_aspects:
#                         continue
#                     format, imgstr = image.split(';base64,')
#                     ext = format.split('/')[-1]
#                     image_data = base64.b64decode(imgstr)
#                     product_image = ProductImage(product=product, aspect=aspect)
#                     product_image.image.save(
#                         f'image.{ext}', ContentFile(image_data), save=True)

#                 # Обновляем дополнительные опции товара
#                 # Удаляем старые опции
#                 product.additional_options.all().delete()
#                 # Добавляем новые опции
#                 for option, value in form_data['additionalOptionsData'].items():
#                     opt_name = AdditionalOptionName.objects.get_or_create(name=option)[
#                         0]
#                     AdditionalOption.objects.create(
#                         name=opt_name, product=product, price=value
#                     )

#                 return JsonResponse({'status': 'success', 'message': 'Товар успешно обновлен'})

#         except Exception as e:
#             print(e)
#             return JsonResponse({'status': 'error', 'message': 'Ошибка при обновлении товара'}, status=400)

#     else:
#         attributes = product.attributes.all()
#         attr_keys = {attr.template.id: attr.key for attr in attributes}
#         attr_values = {attr.template.id: attr.value for attr in attributes}
#         # product_images = {img.aspect: img for img in product.product_images.all()}

#         product_images = dict()
#         for img in product.product_images.all():
#             with open(img.image.path, "rb") as image_file:
#                 encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
#                 product_images[img.aspect] = encoded_string
#                 product_images[img.aspect] = {
#                     'base64': encoded_string,
#                     'format': img.image.name.split('.')[-1],  # Get the file extension (e.g., webp, png, jpg)
#                 }

#         context = {
#             'browser_tab_name': "Редактирование товара",
#             'category': product.category,
#             'product': product,
#             'attr_keys': attr_keys,
#             'attr_values': attr_values,
#             'image_placeholders': IMAGE_PLACEHOLDERS,
#             'product_images': product_images,
#         }

#         return render(request, 'account/manage_products.html', context)


# @login_required
# def delete_product(request, pk):
#     """Удаление товара продавцом."""
#     product = get_object_or_404(Product, pk=pk)
#     product.delete()

#     return redirect(reverse('products'))  # Redirect to the product list after deletion


# def add_to_comparison(request, slug):
#     """Добавляем товар в сравнение (если его там еще нет)"""
#     if request.method != "POST":
#         return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'}, status=405)

#     try:
#         product = Product.objects.get(slug=slug)

#         if request.user.is_authenticated:
#             # Проверяем, есть ли уже товар в сравнении для пользователя
#             existing_entry = Comparison.objects.filter(
#                 product=product, user=request.user).exists()
#             if existing_entry:
#                 return JsonResponse({'status': 'warning', 'message': 'Товар уже в сравнении'})

#             # Добавляем товар
#             Comparison.objects.create(product=product, user=request.user)

#         else:
#             # Работаем с сессией для анонимных пользователей
#             session_key = request.session.session_key
#             if not session_key:
#                 request.session.create()
#                 session_key = request.session.session_key

#             # Проверяем, есть ли товар в сравнении для данной сессии
#             existing_entry = Comparison.objects.filter(
#                 product=product, session_key=session_key).exists()
#             if existing_entry:
#                 return JsonResponse({'status': 'warning', 'message': 'Товар уже в сравнении'})

#             # Добавляем товар
#             Comparison.objects.create(product=product, session_key=session_key)

#         return JsonResponse({'status': 'success', 'message': 'Товар добавлен в сравнение'})

#     except Product.DoesNotExist:
#         return JsonResponse({'status': 'error', 'message': 'Товар не найден'}, status=404)


# @require_http_methods(["DELETE"])
# def remove_from_comparison(request, product_id):
#     """Удаляем товар из сравнения"""
#     try:
#         product = Product.objects.get(id=product_id)  # Ищем по id

#         if request.user.is_authenticated:
#             # Удаляем товар из сравнения для авторизованного пользователя
#             Comparison.objects.filter(
#                 product=product, user=request.user).delete()
#         else:
#             # Удаляем товар из сравнения для анонимного пользователя
#             session_key = request.session.session_key
#             if session_key:
#                 Comparison.objects.filter(
#                     product=product, session_key=session_key).delete()

#         return JsonResponse({'status': 'success', 'message': 'Товар удален из сравнения'})

#     except Product.DoesNotExist:
#         return JsonResponse({'status': 'error', 'message': 'Товар не найден'}, status=404)


# def add_to_favorites(request, slug):
#     """Добавляем товар в избранное"""
#     # Работает но нужен шаблон.
#     if request.method != 'POST':
#         return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'}, status=405)

#     try:
#         product = Product.objects.get(link=slug)

#         if request.user.is_authenticated:
#             # Проверяем, есть ли товар в любимых для пользователя
#             favorite_exists = Favorite.objects.filter(
#                 product=product, user=request.user).exists()
#             if favorite_exists:
#                 return JsonResponse({'status': 'warning', 'message': 'Товар уже в избранном'})

#             # Добавляем товар в избранное
#             Favorite.objects.create(product=product, user=request.user)
#             return JsonResponse({'status': 'success', 'message': 'Товар добавлен в избранное'})
#         else:
#             return JsonResponse({'status': 'warning', 'message': 'Сначала зарегистрируйтесь'})

#     except Product.DoesNotExist:
#         return JsonResponse({'status': 'error', 'message': 'Товар не найден'}, status=404)


# @require_http_methods(["DELETE"])
# def remove_from_favorites(request, product_id):
#     """Удаляем товар из избранного"""
#     # Работает но нужен шаблон.
#     try:
#         product = Product.objects.get(id=product_id)  # Ищем по id

#         if request.user.is_authenticated:
#             Favorite.objects.filter(
#                 product=product, user=request.user).delete()

#         return JsonResponse({'status': 'success', 'message': 'Товар удален из любимых'})

#     except Product.DoesNotExist:
#         return JsonResponse({'status': 'error', 'message': 'Товар не найден'}, status=404)


# @login_required
# def manage_companies(request):
#     """Страница управления компаниями."""
#     # Тестовая версия нужен шалон.
#     user = request.user
#     return render(request, 'account/manage_companies.html', {
#         'user': user,
#         'form_title': 'Добавить компанию',
#         'form_action': '/account/add_company/',
#         'submit_button_text': 'Добавить'
#     })


# @login_required
# def add_company(request):
#     """Добавление новой компании."""
#     # Тестовая версия нужен шалон.
#     if request.method == 'POST':
#         form = CompanyForm(request.POST)
#         if form.is_valid():
#             company = form.save(commit=False)
#             company.user = request.user
#             company.save()
#             request.user.companys.add(company)
#             messages.success(request, f"Компания '{company.name}' успешно добавлена.")
#             return redirect('manage_companies')
#     else:
#         form = CompanyForm()
#     return render(request, 'account/manage_companies.html', {
#         'form': form,
#         'form_title': 'Добавить компанию',
#         'form_action': '/account/add_company/',
#         'submit_button_text': 'Добавить'
#     })


# @login_required
# def edit_company(request, company_id):
#     """Редактирование компании."""
#     # Тестовая версия нужен шалон.
#     company = get_object_or_404(Company, id=company_id, user=request.user)
#     if request.method == 'POST':
#         form = CompanyForm(request.POST, instance=company)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f"Компания '{company.name}' успешно обновлена.")
#             return redirect('manage_companies')
#     else:
#         form = CompanyForm(instance=company)
#     return render(request, 'account/manage_companies.html', {
#         'form': form,
#         'form_title': 'Редактировать компанию',
#         'form_action': f'/account/edit_company/{company_id}/',
#         'submit_button_text': 'Сохранить'
#     })


# @login_required
# def remove_company(request, company_id):
#     """Удаление компании."""
#     # Тестовая версия нужен шалон.
#     company = get_object_or_404(Company, id=company_id, user=request.user)
#     request.user.companys.remove(company)
#     messages.success(request, f"Компания '{company.name}' успешно удалена.")
#     return redirect('manage_companies')

# # @login_required
# # def order_card(request, order_number):

# #     translation.activate('ru')

# #     order = Order.objects.filter(number=order_number).first()

# #     additional_options = AdditionalOption.objects.filter(
# #         id__in=order.selected_additional_options)

# #     additional_options_price = additional_options.aggregate(
# #         total=Sum('price'))['total'] or 0

# #     base_price = order.product.cur_price

# #     order_price = additional_options_price + base_price

# #     base_price_pr = round((base_price / order_price)*100, 0)

# #     down_payment = round(order_price * order.down_payment_percent / 100, 0)

# #     context = {'view_id': 'order',
# #                'order': order,
# #                'additional_options': additional_options,
# #                'additional_options_price': additional_options_price,
# #                'order_price': order_price,
# #                'base_price_pr': base_price_pr,
# #                'down_payment': down_payment,
# #                'browser_tab_name': "Просмотр заказа", }

# #     return render_or_main_fetch(
# #         request, 'account/index.html', context)

# # def question_and_reviews_view(request):
# #     questions = Question.objects.filter(username=request.user)
# #     reviews = ProductReview.objects.filter(user=request.user)

# #     print("Вопросы:", questions)  # Отладка
# #     print("Отзывы:", reviews)  # Отладка

# #     context = {
# #         'browser_tab_name': "Отзывы и вопросы",
# #         'questions': questions,
# #         'reviews': reviews,
# #     }
# #     return render_or_main_fetch(request, 'account/index.html', context)