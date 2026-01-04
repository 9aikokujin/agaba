import logging
import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from messenger.models import Notification


def send_notification(user_id, message_type, data=None):
    """Отправляет уведомление и сохраняет его в базе."""
    from django.utils import timezone
    from account.models import CustomUser

    try:
        user = CustomUser.objects.get(id=user_id)

        notification_data = {
            'type': message_type,
            'data': {
                k: str(v) for k, v in (data or {}).items()
            },
            'timestamp': str(timezone.now())
        }

        json.dumps(notification_data)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user_id}',
            {
                'type': 'send_notification',
                'content': notification_data
            }
        )

        Notification.objects.create(
            user=user,
            message=notification_data
        )

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка отправки уведомления: {e}", exc_info=True)
