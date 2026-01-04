from rest_framework.exceptions import PermissionDenied

from rest_framework import permissions


class AuthorOrAdminPermissionMixin:
    """
    Миксин для проверки прав доступа.
    Разрешает доступ только автору объекта или администратору для изменений,
    но разрешает просмотр всем для GET-запросов.
    """
    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        # Разрешаем доступ всем для безопасных методов (GET, HEAD, OPTIONS)
        if self.request.method in permissions.SAFE_METHODS:
            return obj
        # Для остальных методов проверяем права

        if obj.author != user and not user.is_staff:
            raise PermissionDenied(
                "Вы не имеете права изменять или удалять этот объект."
            )
        return obj
