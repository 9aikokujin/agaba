from . import views
from django.urls import path

urlpatterns = [
    # Пополнение баланса
    # path('form_for_replenishment/', views.form_for_replenishment, name='form_for_replenishment'),
    # # Вывод средств
    # path('form_for_withdrawal/', views.form_for_withdrawal, name='form_for_withdrawal'),
    # Получение компаний при вводе ИНН или Названия компании
    path('get_company_info/', views.get_company_info, name='get_company_info'),
]