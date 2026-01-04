from django import template

register = template.Library()


@register.filter(name='get')
def get(dictionary, key):
    """Безопасно получить значение словаря по ключу, возвращая пустую строку при ошибке."""

    try:
        return dictionary.get(key, '')
    except AttributeError:
        return ''
