# Для настройки Celary определение модера онлайн(еще пригодиться)

# from celery import shared_task
# from django.core.exceptions import ValidationError

# @shared_task(bind=True, max_retries=5)
# def assign_moderator_task(self):
#     online_moderators = Moderator.objects.filter(
#         is_online=True,
#         is_responsible_for_delivery=True
#     )
    
#     if online_moderators.exists():
#         return random.choice(online_moderators).id
#     else:
#         # Если модераторов нет, повторяем попытку через некоторое время
#         raise self.retry(countdown=10)  # Повторить через 10 секунд
