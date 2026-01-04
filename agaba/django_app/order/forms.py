# from decimal import Decimal
# from django import forms
# from .models import Order, DeliveryOrder

# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = [
#             'product', 'user', 'address', 'company', 'payment_type',
#             'down_payment_percent', 'amount', 'selected_additional_options'
#         ]
#         widgets = {
#             'product': forms.HiddenInput(),
#             'user': forms.HiddenInput(),
#             'company': forms.Select(attrs={'class': 'form-control'}),
#             'payment_type': forms.HiddenInput(),
#             'address': forms.TextInput(),
#             'down_payment_percent': forms.NumberInput(attrs={'class': 'slider_input'}),
#             'amount': forms.HiddenInput(),
#             'selected_additional_options': forms.CheckboxSelectMultiple(),
#         }

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         product = kwargs.pop('product', None)
#         total_amount = kwargs.pop('total_amount', None)
#         selected_options_queryset = kwargs.pop('selected_options_queryset', None)
#         super().__init__(*args, **kwargs)

#         # Устанавливаем начальные значения
#         if user:
#             self.fields['user'].initial = user.id
#         if product:
#             self.fields['product'].initial = product.id
#         if total_amount:
#             self.fields['amount'].initial = total_amount

#         # Ограничиваем выбор компаний только теми, которые доступны пользователю
#         if user and hasattr(user, 'companies'):
#             self.fields['company'].queryset = user.companies.all()

#         # Ограничиваем выбор дополнительных опций только теми, которые доступны для продукта
#         if product:
#             self.fields['selected_additional_options'].queryset = product.additional_options.all()

#         # Если переданы выбранные опции, устанавливаем их как начальное значение
#         if selected_options_queryset:
#             self.fields['selected_additional_options'].initial = selected_options_queryset

#         # Делаем поле selected_additional_options необязательным
#         self.fields['selected_additional_options'].required = False

#     def clean(self):
#         """
#         Выполняем проверки и расчет first_payment на основе down_payment_percent.
#         """
#         cleaned_data = super().clean()
#         amount = cleaned_data.get('amount')
#         down_payment_percent = cleaned_data.get('down_payment_percent')

#         # Проверяем, что amount и down_payment_percent заданы
#         if amount is None or down_payment_percent is None:
#             raise forms.ValidationError("Значения amount и down_payment_percent должны быть заданы.")

#         # Проверяем, что значения не отрицательные
#         if amount < 0 or down_payment_percent < 0:
#             raise forms.ValidationError("Значения amount и down_payment_percent не могут быть отрицательными.")

#         # Рассчитываем first_payment
#         cleaned_data['first_payment'] = (Decimal(amount) * Decimal(down_payment_percent)) / Decimal(100)

#         return cleaned_data

#     def save(self, commit=True):
#         """
#         Сохраняем объект модели с рассчитанным значением first_payment.
#         """
#         # Получаем объект Order из родительского метода save
#         order = super().save(commit=False)

#         # Устанавливаем значение first_payment из очищенных данных
#         order.first_payment = self.cleaned_data.get('first_payment')

#         # Сохраняем объект, если commit=True
#         if commit:
#             order.save()

#         return order
    

# # class DeliveryOrderForm(forms.ModelForm):
# #     class Meta:
# #         model = DeliveryOrder
# #         fields = [
# #             'delivery_stage',
# #             'delivery_type',
# #             'amount',
# #             'dimensions',
# #             'date_delivery',
# #             'address_delivery',
# #             # 'manager',
# #         ]
# #         widgets = {
# #             'date_delivery': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
# #         }