# from babel.numbers import format_currency
# from babel.dates import format_date
# from django import template
# from datetime import datetime

# register = template.Library()

# @register.filter
# def format_rubles(value):

#     if not value:
#         value = 0

#     value = round(value, 0)

#     return format_currency(
#         value, 'RUB', locale='ru_RU').replace(',00', '')


# @register.filter
# def format_russian_date(value):
#     return format_date(value, format='long', locale='ru_RU').rstrip(' г.')