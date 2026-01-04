from django.db import models
from django.utils import timezone
from account.models import CustomUser


class Notification(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.JSONField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"Notification for {
            self.user.username
        } - {self.message.get('type', 'no-type')}"

    @classmethod
    def create_notification(cls, user, message_type, data=None):
        message = {
            'type': message_type,
            'data': dict(data) if data else {},
            'timestamp': str(timezone.now())
        }

        try:
            import json
            json.dumps(message)
        except TypeError as e:
            raise ValueError(
                f"Невозможно сериализовать данные уведомления: {e}"
            )

        return cls.objects.create(
            user=user,
            message=message
        )


class Chat(models.Model):
    ORDER_CHAT = 'order'
    PRODUCT_CHAT = 'product'
    SUPPORT_CHAT = 'support'

    CHAT_TYPE_CHOICES = [
        (ORDER_CHAT, 'Order Chat'),
        (PRODUCT_CHAT, 'Product Chat'),
        (SUPPORT_CHAT, 'Support Chat'),
    ]

    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='chats'
    )
    participants = models.ManyToManyField(CustomUser, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat', 'is_read']),
            models.Index(fields=['sender', 'chat']),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} in chat {self.chat.id}"
