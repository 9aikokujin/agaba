import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from django_app.kafka import publish_event

logger = logging.getLogger(__name__)


def _operation_payload(operation, event_type):
    return {
        "event_type": event_type,
        "event_version": 1,
        "source": "balance.AllOperation",
        "operation": {
            "id": str(operation.operation_id),
            "type": operation.type_operation,
            "status": operation.status_operation,
            "payment_type": operation.payment_type,
            "amount": str(operation.amount) if operation.amount is not None else None,
            "user_id": operation.user_id,
            "replenishment_id": (
                str(operation.replenishment_id)
                if operation.replenishment_id
                else None
            ),
            "withdrawal_id": (
                str(operation.withdrawal_id) if operation.withdrawal_id else None
            ),
            "order_operation_id": (
                str(operation.order_operation_id)
                if operation.order_operation_id
                else None
            ),
        },
        "details": operation.details or {},
        "created_at": (
            operation.date_created.isoformat()
            if getattr(operation, "date_created", None)
            else None
        ),
        "updated_at": (
            operation.date_modified.isoformat()
            if getattr(operation, "date_modified", None)
            else None
        ),
        "occurred_at": timezone.now().isoformat(),
    }


def publish_operation_event(operation, event_type):
    if not getattr(settings, "KAFKA_ENABLED", False):
        return

    topic = getattr(settings, "KAFKA_OPERATION_TOPIC", None)
    if not topic:
        return

    def _publish():
        payload = _operation_payload(operation, event_type)
        sent = publish_event(topic, payload, key=operation.operation_id)
        if not sent:
            logger.debug(
                "Событие Kafka пропущено для операции %s", operation.operation_id
            )

    transaction.on_commit(_publish)
