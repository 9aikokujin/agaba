from django.apps import AppConfig


class BalanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'balance'

    def ready(self):
        """
        Этот метод вызывается при готовности приложения.
        Здесь мы импортируем сигналы, чтобы они были зарегистрированы.
        """
        import balance.signals