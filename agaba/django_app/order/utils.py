# ВАЖНО! Выбиаем последнего активного менеджера (ограниечение кол-ва заказов привязанных???).
# Правила выбора из Фигмы.
from django.utils import timezone
from account.models import CustomUser


def assign_manager():
    """
    Выбирает менеджера на основе онлайн-статуса и шанса 50%.
    """
    twenty_four_hours_ago = timezone.now() - timezone.timedelta(hours=24)

    # Получаем всех менеджеров, которые были онлайн за последние 24 часа
    managers = CustomUser.objects.filter(
        role='manager',
        last_seen__gte=twenty_four_hours_ago
    ).order_by('id')

    if not managers.exists():
        return None

    for manager in managers:
        if timezone.now().microsecond % 2 == 0:
            return manager
    print(f'Добавлен менеджер {managers.first()} в список по шансу 50%')
    return managers.first()
