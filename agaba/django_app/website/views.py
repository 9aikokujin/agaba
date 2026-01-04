# from .models import Product, AdditionalOption, Question, ProductReview, CustomUser, Category
# from django.shortcuts import render, HttpResponse, redirect
# from django.http import JsonResponse
# import json
# import re
# from decimal import Decimal
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from datetime import datetime
# from .utils import render_or_main_fetch
# from django.db.models import Q, Count, Case, When, Value, IntegerField
# from django.template.loader import render_to_string
# from django.views.decorators.csrf import csrf_exempt
# from django.shortcuts import get_object_or_404
# #Изменения
# from django.views import View

# from .forms import QuestionForm
# from django.contrib.auth.decorators import login_required
# from collections import defaultdict
# from django.conf import settings

# FILTER_CONDITIONS = [('new', 'Новое'), ('used', 'Б/у'), ('spare_parts', 'На з/ч')]
# FILTER_DELIVERY_TIMES = [('7_13', '7-13 дней'), ('14_27', '14-27 дней'), ('>28', '28 и более дней')]


# def index(request):

#     products = Product.objects.filter(
#         in_stock=True, mod_status='active').order_by('-created')[:20]

#     context = {
#         'browser_tab_name': "AGABA Главная",
#         'products': products,
#         'adverts_small': [f'_{i}.png' for i in range(1, 6)],
#         'adverts_large': ('__1.png', '__2.png'),
#     }

#     return render(request, 'website/base.html', context)


# def catalog(request, slug):
#     category = get_object_or_404(Category, slug=slug)
#     brands = Product.objects.values('brand').distinct()
#     conditions = Product.objects.values('condition').distinct()
#     delivery_time_days = Product.objects.values('delivery_time_days').distinct()

#     context = {'category': category,
#                'brands': brands,
#                'conditions': conditions,
#                'delivery_time_days': delivery_time_days,
#                'adverts_small': [f'_{i}.png' for i in range(1, 6)],
#                'browser_tab_name': category.name}

#     products = category.get_products()

#     # Список годов для фильтра
#     filter_years = sorted(list(products.values_list(
#         'prod_year', flat=True).distinct().order_by('prod_year')))
#     # Данные для выпадающих списков фильтров (цена, год, состояние, срок доставки)
#     context['filters'] = {
#         'cur_price': [(price, price) for price in range(0, 999999, 100)],
#         'prod_year': [(year, year) for year in filter_years],
#         'condition': FILTER_CONDITIONS.copy(),
#         'delivery_time_days': FILTER_DELIVERY_TIMES.copy(),
#     }
#     # Добавляем опцию "Все" в каждый фильтр
#     for key in context['filters']:
#         context['filters'][key].insert(0, ('all', 'Все'))

#     # Получаем фильтры из запроса
#     filters = request.GET.get('filters')
#     # print(filters)
#     if filters:
#         filters = json.loads(filters)
#         django_filters, query = dict(), Q()
#         # Процессинг фильтров
#         for k, v in filters.items():
#             if 'all' in v:
#                 continue

#             if k == 'cur_price':
#                 # Обрабатываем фильтры для цены
#                 if 'from' in v:
#                     query &= Q(cur_price__gte=Decimal(v['from']))
#                 if 'to' in v:
#                     query &= Q(cur_price__lte=Decimal(v['to']))

#             elif k == 'delivery_time_days':
#                 for i in v:
#                     print(f"Обрабатываем фильтр по доставке: {i}")  # Отладка фильтра

#                     if i.startswith('up_to_'):  # Фильтр "до X дней"
#                         try:
#                             max_value = int(i.replace('up_to_', ''))  # Преобразуем в число
#                             print(f"Фильтр: {k} <= {max_value}")
#                             query |= Q(**{f"{k}__lte": max_value})  # Применяем фильтрацию
#                         except ValueError:
#                             print(f"Ошибка преобразования числа (up_to_): {i}")
#                             continue  # Пропускаем ошибочные значения

#                     elif '_' in i:  # Фильтр диапазона "X_Y"
#                         try:
#                             start, end = map(int, i.split('_'))  # Преобразуем в числа
#                             print(f"Фильтр: {k} между {start} и {end}")
#                             query |= Q(**{f"{k}__range": (start, end)})  # Применяем диапазон
#                         except ValueError:
#                             print(f"Ошибка преобразования числа (_): {i}")
#                             continue  # Пропускаем ошибочные значения

#                     elif i.startswith('>'):  # Фильтр "более X дней"
#                         try:
#                             days = int(i[1:])  # Преобразуем в число
#                             print(f"Фильтр: {k} >= {days}")
#                             query |= Q(**{f"{k}__gte": days})  # Применяем фильтрацию
#                         except ValueError:
#                             print(f"Ошибка преобразования числа (>): {i}")
#                             continue  # Пропускаем ошибочные значения

#             else:
#                 django_filters[k + '__in'] = v

#         # Применяем фильтры
#         products = products.filter(query) if query else products
#         if django_filters:
#             products = products.filter(**django_filters)
#     else:
#         products = products.filter(in_stock=True)

#     # Пагинация товаров
#     page = request.GET.get('page', 1)
#     products = products.order_by('name')

#     if settings.DEBUG:
#         # temp multiple for testing
#         products = list(products)*100

#     # Формируем отображение товаров для корневых и дочерних категорий
#     if category.parent is not None:
#         context['is_root_category'] = False
#         paginator = Paginator(products, 15)
#     else:
#         context['is_root_category'] = True
#         paginator = Paginator(products, 20)

#     try:
#         products = paginator.page(page)
#     except PageNotAnInteger:
#         products = paginator.page(1)
#     except EmptyPage:
#         products = paginator.page(paginator.num_pages)

#     context['products'] = products

#     # Обработка нажатия кнопки "Показать еще"
#     fetch_template_name = None
#     if request.GET.get('show_more') or request.GET.get('processFilter'):
#         fetch_template_name = 'website/_catalog_list_fetch.html'

#     return render_or_main_fetch(
#         request, 'website/catalog.html', context, fetch_template_name)


# def search_products(request):
#     """Поиск товаров."""
#     query = request.GET.get('q', '').strip()
#     # print(query)

#     if not query:
#         raise ValueError("Пустой запрос поиска")

#     # Search products with a single query
#     products = Product.objects.filter(
#         Q(brand__icontains=query) | 
#         Q(name__icontains=query) | 
#         Q(description__icontains=query)
#     ).select_related('category')

#     print(products)

#     # Разбиваем товары по категориям
#     categories = defaultdict(list)
#     for product in products:
#         categories[product.category].append(product)

#     # Сортируем категории по количеству товаров
#     categories_count = [
#         (category, len(category_products))
#         for category, category_products in sorted(
#             categories.items(),
#             key=lambda item: len(item[1]),
#             reverse=True
#         )
#     ]

#     # Сохраняем результаты поиска в сессии
#     request.session['search_results'] = {
#         # 'categories_count': {
#         #     category.id: products.count() for category, products in categories.items()},
#         'products': [product.id for product in products],
#         'query_request': query,
#     }

#     context = {
#         'products': products[:3],
#         'count': products.count(),
#         'categories': categories_count
#     }

#     return HttpResponse(render_to_string('website/_search_modal.html', context))


# def search_results(request):
#     """Display search results."""
#     # Get search results from session
#     search_results = request.session.get('search_results', {})
#     query_request = search_results.get('query_request', '')

#     # print(search_results)
    
#     # if slug not in search_results:
#     #     return HttpResponse(status=404)

#     # Get products and category in single query
#     products = Product.objects.filter(
#         id__in=search_results['products']
#     ).select_related('category')

#     products_count = products.count()
    
#     if not products.exists():
#         return HttpResponse(status=404)

#     category = products[0].category  # All products share the same category

#     context = {
#         # 'category': category,
#         'query_request': query_request,
#         # 'products': products,
#         'products_count': products_count,
#         'browser_tab_name': "Поиск товаров",
#     }

#     # Список годов для фильтра
#     filter_years = sorted(list(products.values_list(
#         'prod_year', flat=True).distinct().order_by('prod_year')))
#     # Список брендов для фильтра
#     filter_brands = sorted(list(products.values_list(
#         'brand', flat=True).distinct().order_by('brand')))
#     # Данные для выпадающих списков фильтров (цена, год, состояние, срок доставки)
#     context['filters'] = {
#         'brand': [(brand, brand) for brand in filter_brands],
#         'prod_year': [(year, year) for year in filter_years],
#         'condition': FILTER_CONDITIONS.copy(),
#         'delivery_time_days': FILTER_DELIVERY_TIMES.copy(),
#     }
#     # print(context['filters'])
#     # Добавляем опцию "Все" в каждый фильтр
#     for key in context['filters']:
#         context['filters'][key].insert(0, ('all', 'Все'))

#     # Пагинация товаров
#     page = request.GET.get('page', 1)
#     products = products.order_by('name')

#     if settings.DEBUG:
#         # temp multiple for testing
#         products = list(products)*100

#     paginator = Paginator(products, 15)
#     try:
#         products = paginator.page(page)
#     except PageNotAnInteger:
#         products = paginator.page(1)
#     except EmptyPage:
#         products = paginator.page(paginator.num_pages)

#     context['products'] = products

#     # Обработка нажатия кнопки "Показать еще"
#     fetch_template_name = None
#     if request.GET.get('show_more') or request.GET.get('processFilter'):
#         fetch_template_name = 'website/_search_list_fetch.html'

#     return render_or_main_fetch(
#         request, 'website/search_results.html', context, fetch_template_name)


# def product_card(request, slug):
#     # product = Product.objects.filter(slug=slug).first()
#     product = get_object_or_404(Product, slug=slug)
#     questions = Question.objects.filter(product=product)
#     reviews = ProductReview.objects.filter(product=product)

#     # Get the list of recently viewed product IDs from the session
#     recently_viewed_products = request.session.get('recently_viewed_products', [])

#     # Add the current product ID to the list
#     if product.id not in recently_viewed_products:
#         recently_viewed_products.insert(0, product.id)

#     # Ensure the list does not exceed 5 items
#     recently_viewed_products = recently_viewed_products[:5]

#     # Update the session with the new list
#     request.session['recently_viewed_products'] = recently_viewed_products

#     request.session['slug'] = slug

#     # Get the actual Product objects for the recently viewed products
#     recently_viewed_products_objects = Product.objects.filter(
#         id__in=recently_viewed_products
#     )

#     # Поиск похожих товаров с приоритетами
#     similar_products = Product.objects.filter(
#         category=product.category  # Фильтруем только по текущей группе
#     ).annotate(
#         priority=Case(
#             # Высший приоритет: тот же бренд и группа
#             When(brand=product.brand, category=product.category, then=Value(1)),
#             # Средний приоритет: та же группа, но другой бренд
#             When(category=product.category, then=Value(2)),
#             # # Низший приоритет: та же подгруппа
#             # When(subgroup=product.subgroup, then=Value(3)),
#             output_field=IntegerField(),
#         )
#     ).exclude(id=product.id).order_by('priority')[:5]  # Ограничиваем общее количество до 5

#     print(similar_products)  # Для отладки

#     context = {
#         'questions': questions,
#         'reviews': reviews,
#         'product': product,
#         'browser_tab_name': product.name,
#         'recently_viewed_products': recently_viewed_products_objects,
#         'similar_products': similar_products,
#     }

#     return render(request, 'website/product_card.html', context)


# def fetch_order_price(request):
#     if request.method == 'POST':

#         data = json.loads(request.body)
#         order_price = data.get('order_price').replace('\xa0', ' ')
#         order_price = re.sub(r'\D', '', order_price)
#         slug = data.get('slug')
#         request.session[slug] = order_price

#     return JsonResponse({'status': 'success'})


# def product_review(request, slug):
#     """Вопросы к товару."""
#     product = Product.objects.filter(slug=slug).first()
#     question_list = Question.objects.filter(product=product)
#     reviews = ProductReview.objects.filter(product=product)
#     context = {
#         'product': product,
#         'browser_tab_name': product.name,
#         'slug': slug,
#         'question_list': question_list,
#         'reviews': reviews
#     }

#     if request.method == 'POST':
#         form = QuestionForm(request.POST)

#         if form.is_valid():
#             question = form.save(commit=False)
#             question.product = product
#             question.save()

#             # Очищаем временные данные сессии
#             request.session.pop('question_data', None)
#             request.session.pop('slug', None)
#             request.session.pop('next', None)

#             context['form'] = QuestionForm()
#             context['success_message'] = "Ваш вопрос был успешно отправлен!"

#             return render(request, 'website/product_review.html', context)

#         else:
#             # Если ошибка из-за username, редиректим на регистрацию
#             if "username" in form.errors:
#                 request.session['question_data'] = request.POST
#                 request.session['slug'] = slug
#                 request.session['next'] = request.path
#                 print("❌ Пользователь не найден. Редирект на регистрацию.")
#                 return redirect('auth_user')  # 🔹 Редирект на регистрацию

#             print("❌ Ошибка валидации формы:", form.errors)  # Выводим ошибки формы
#             context['form'] = form

#     else:
#         # Восстанавливаем данные формы после регистрации
#         initial_data = request.session.pop('question_data', {})
#         form = QuestionForm(initial=initial_data)

#         context['form'] = form

#     return render(request, 'website/product_review.html', context)
