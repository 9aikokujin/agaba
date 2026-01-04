from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from messenger.models import Chat, Message

CustomUser = get_user_model()


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Получает websocket для пользовательских уведомлений."""
    async def connect(self):
        """Проверяет токен и подключает к группе пользователя."""
        self.user = None
        self.notification_group_name = None

        token = self.scope['query_string'].decode().split('=')[1]

        if not token:
            await self.close(code=4001)
            return

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await self.get_user(user_id)

            if not self.user:
                await self.close(code=4001)
                return

            self.notification_group_name = f'notifications_{self.user.id}'

            await self.channel_layer.group_add(
                self.notification_group_name,
                self.channel_name
            )

            await self.accept()

        except (TokenError, IndexError, KeyError):
            await self.close(code=4001)

    async def disconnect(self, close_code):
        """Покидает группу уведомлений при отключении."""
        if self.notification_group_name:
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        """Игнорирует входящие данные."""
        pass

    async def send_notification(self, event):
        """Отправляет уведомление клиенту."""
        await self.send_json(event['content'])

    @database_sync_to_async
    def get_user(self, user_id):
        """Возвращает пользователя по id."""
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """Получает websocket чата для комнаты."""
    async def connect(self):
        """Проверяет токен и подключает к группе чата."""
        self.user = None
        self.chat_id = None
        self.chat_group_name = None

        token = self.scope['query_string'].decode().split('=')[1]
        if not token:
            await self.close(code=4001)
            return

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await self.get_user(user_id)
            if not self.user:
                await self.close(code=4001)
                return

            self.chat_id = self.scope['url_route']['kwargs']['chat_id']
            if not await self.is_participant(self.chat_id, self.user):
                await self.close(code=4003)
                return

            self.chat_group_name = f'chat_{self.chat_id}'
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            await self.accept()
        except (TokenError, IndexError, KeyError):
            await self.close(code=4001)

    async def disconnect(self, close_code):
        """Покидает группу чата при отключении."""
        if self.chat_group_name:
            await self.channel_layer.group_discard(
                self.chat_group_name,
                self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        """Обрабатывает входящие сообщения чата."""
        message_type = content.get('type')

        if message_type == 'chat_message':
            message = content.get('message')
            if message:
                saved_message = await self.save_message(message)

                await self.channel_layer.group_send(
                    self.chat_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': saved_message.id,
                            'sender': saved_message.sender.id,
                            'content': saved_message.content,
                            'created_at': saved_message.created_at.isoformat(),
                            'is_read': saved_message.is_read
                        }
                    }
                )

    async def chat_message(self, event):
        """Отправляет сообщение чата клиенту."""
        await self.send_json({
            'type': 'chat_message',
            'message': event['message']
        })

    @database_sync_to_async
    def get_user(self, user_id):
        """Возвращает пользователя по id."""
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None

    @database_sync_to_async
    def is_participant(self, chat_id, user):
        """Проверяет, что пользователь участник чата."""
        return Chat.objects.filter(id=chat_id, participants=user).exists()

    @database_sync_to_async
    def save_message(self, message_text):
        """Сохраняет новое сообщение чата."""
        chat = Chat.objects.get(id=self.chat_id)
        message = Message.objects.create(
            chat=chat,
            sender=self.user,
            content=message_text
        )
        return message
