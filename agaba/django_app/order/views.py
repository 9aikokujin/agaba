# from decimal import Decimal
# from datetime import timedelta

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import ValidationError
# from django.db.models import Sum
# from django.shortcuts import render, get_object_or_404, redirect
# from django.utils.timezone import now

# from .forms import OrderForm
# from .models import Order, OrderManagerAssignment, DeliveryOrder
# from .utils import assign_manager
# from website.models import Product, AdditionalOption, Company


# @login_required
# def create_order(request, product_slug):
#     """Создание заказа"""
#     product = get_object_or_404(Product, slug=product_slug)
#     user = request.user

#     # Логика для выбранных опций
#     if request.method == 'POST':
#         selected_option_ids = request.POST.get('selected_options', '').split(',')
#     else:
#         selected_option_ids = request.GET.get('selected_options', '').split(',')

#     selected_option_ids = [option_id.strip() for option_id in selected_option_ids if option_id.strip().isdigit()]
#     try:
#         selected_option_ids = [int(option_id) for option_id in selected_option_ids]
#     except ValueError:
#         raise ValidationError("Invalid selected options.")

#     selected_options = (
#         AdditionalOption.objects.filter(id__in=selected_option_ids, product=product)
#         if selected_option_ids
#         else AdditionalOption.objects.none()
#     )

#     additional_options_price = (
#         selected_options.aggregate(total_price=Sum('price'))['total_price'] or 0
#     )
#     total_amount = product.cur_price + additional_options_price

#     if request.method == 'POST':
#         form = OrderForm(
#             request.POST,
#             user=user,
#             product=product,
#             total_amount=total_amount,
#             selected_options_queryset=selected_options,
#         )

#         if form.is_valid():
#             order = form.save(commit=False)
#             order.product = product
#             order.user = user
#             order.payment_type = request.POST.get('payment_type', 'is_cash')
#             order.address = request.POST.get('address', '').strip()  # Обработка address
#             order.amount = total_amount

#             # Сохраняем заказ
#             order.save()

#             # Назначаем менеджера
#             manager = assign_manager()
#             if manager:
#                 OrderManagerAssignment.objects.create(order=order, manager=manager)

#             if selected_options.exists():
#                 order.selected_additional_options.set(selected_options)
#             else:
#                 order.selected_additional_options.clear()

#             return redirect('orders')  # Потом поменять на заказ, который был создан.
#         else:
#             context = {
#                 'form': form,
#                 'product': product,
#                 'companies': list(user.companies.all()) or [],
#                 'selected_options': list(selected_options),
#                 'total_amount': total_amount,
#                 'address': request.POST.get('address', ''),  # Корректная обработка address
#                 'selected_options_ids': selected_option_ids,
#                 'form_errors': form.errors,
#             }
#             return render(request, 'website/create_order.html', context)
#     else:
#         form = OrderForm(
#             user=user,
#             product=product,
#             total_amount=total_amount,
#             selected_options_queryset=selected_options,
#             initial={'address': request.GET.get('address', '')},  # Передача начального значения
#         )

#     context = {
#         'form': form,
#         'product': product,
#         'companies': list(user.companies.all()) or [],
#         'selected_options': list(selected_options),
#         'total_amount': total_amount,
#         'selected_options_ids': selected_option_ids,
#         'address': request.GET.get('address', ''),  # Корректная обработка address
#     }
#     return render(request, 'website/create_order.html', context)

# @login_required
# def order_first_step(request, number):
#     """Певая ступень заказа."""
#     order = Order.objects.filter(number=number).first()
#     options = order.selected_additional_options.all()
#     images = order.product.product_images.all()
#     order_stage = order.stage
#     date_delivery = order.product.delivery_time_days
#     delivery_number = order.delivery_number
#     context = {
#         'order': order,
#         'order_stage': order_stage,
#         'images': images,
#         'options': options,
#         'date_delivery': date_delivery,
#         'delivery_number': delivery_number,
#         }

#     return render(request, 'account/order_first_step.html', context)

# @login_required
# def create_delivery_order(request, number):
#     """Создание заявки на доставку."""
#     if request.method == 'POST':
#         # Получаем данные из POST-запроса
#         product_name = request.POST.get('cargo')
#         delivery_time_days = request.POST.get('date_delivered')
#         amount = request.POST.get('amount')
#         address_delivery = request.POST.get('address_delivery')
#         company_name = request.POST.get('order')
#         dimensions = request.POST.get('dimensions')

#         # Отладочный вывод для проверки значений
#         print(f"slug: {product_name}")
#         print(f"delivery_time_days: {delivery_time_days}")
#         print(f"amount: {amount}")
#         print(f"company_name: {company_name}")
#         print(f"address_delivery: {address_delivery}")
        
#         delivery_time_days = int(delivery_time_days)

#         # Обрабатываем значение amount
#         amount = amount.replace(',', '.')
#         amount = Decimal(amount)

#         product = Product.objects.get(slug=product_name)
#         company = Company.objects.get(name=company_name)
#         order = Order.objects.get(delivery_number=number)
#         # Рассчитываем дату доставки: текущая дата + количество дней
#         date_delivery = now() + timedelta(days=delivery_time_days)

#         # Создаем запись о доставке в БД
#         try:
#             print("Attempting to create DeliveryOrder...")
#             delivery_order = DeliveryOrder.objects.create(
#                 number=number,
#                 date_created=now(),
#                 user=request.user,
#                 amount=amount,
#                 date_delivery=date_delivery,  # Рассчитанная дата доставки
#                 cargo=product,
#                 company=company,  # Передаем объект Company
#                 address_delivery=address_delivery,
#                 order=order,
#                 dimensions=dimensions,
#             )
#             print(f"Заказ создан: {delivery_order}")
#             messages.success(request, f'Заказ успешно создан! Номер заказа: {number}')

#             # Перенаправляем на страницу карточки доставки
#             return redirect('delivery_card', number=delivery_order.number)

#         except Exception as e:
#             print(f"Ошибка при создании заказа: {e}")
#             messages.error(request, f'Ошибка при создании заказа: {e}')
#             return redirect('order_first_step', number=number)  # Перенаправляем обратно на форму

#     return render(request, 'account/order_first_step.html', {'number': number})


# def delivery_card(request, number):
#     """Отображение отдельного заказа."""
#     delivery_order = DeliveryOrder.objects.filter(number=number).first()
#     print(delivery_order.dimensions)

#     context = {
#         'delivery_order': delivery_order,
#     }

#     return render(request, 'account/delivery_card.html', context)
