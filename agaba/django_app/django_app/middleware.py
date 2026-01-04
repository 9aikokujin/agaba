
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth.models import AnonymousUser


class JWTWebsocketMiddleware:
    """Подставляет пользователя в scope по JWT-токену."""
    def __init__(self, app):
        """Сохраняет обернутое ASGI-приложение."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Определяет пользователя по токену из query-параметров."""

        query_string = scope.get('query_string', b'').decode()
        token_param = [param.split('=') for param in query_string.split('&')]
        token = next(
            (value for key, value in token_param if key == 'token'), None
        )

        if token:
            try:
                jwt_auth = JWTAuthentication()
                validated_token = await database_sync_to_async(
                    jwt_auth.get_validated_token
                )(token)
                user = await database_sync_to_async(
                    jwt_auth.get_user
                )(validated_token)
                scope['user'] = user
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)
