import json
import logging

from django.conf import settings

try:
    from kafka import KafkaProducer
except Exception:
    KafkaProducer = None

logger = logging.getLogger(__name__)
_producer = None


def _bootstrap_servers():
    servers = getattr(settings, "KAFKA_BOOTSTRAP_SERVERS", "")
    if isinstance(servers, str):
        return [item.strip() for item in servers.split(",") if item.strip()]
    return servers or []


def kafka_enabled():
    return bool(getattr(settings, "KAFKA_ENABLED", False))


def get_kafka_producer():
    global _producer
    if not kafka_enabled():
        return None
    if KafkaProducer is None:
        logger.warning("Kafka включена, но без пакета питона.")
        return None
    if _producer is None:
        servers = _bootstrap_servers()
        if not servers:
            logger.warning("Kafka включена, но список bootstrap-серверов пуст.")
            return None
        _producer = KafkaProducer(
            bootstrap_servers=servers,
            client_id=getattr(settings, "KAFKA_CLIENT_ID", None),
            acks=getattr(settings, "KAFKA_ACKS", "all"),
            retries=getattr(settings, "KAFKA_RETRIES", 5),
            linger_ms=getattr(settings, "KAFKA_LINGER_MS", 50),
            max_in_flight_requests_per_connection=getattr(
                settings, "KAFKA_MAX_IN_FLIGHT", 5
            ),
        )
    return _producer


def publish_event(topic, payload, key=None, headers=None):
    producer = get_kafka_producer()
    if producer is None:
        return False

    value = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    key_bytes = None if key is None else str(key).encode("utf-8")
    try:
        producer.send(topic, key=key_bytes, value=value, headers=headers)
        return True
    except Exception:
        logger.exception("Не удалось отправить сообщение в Kafka.")
        return False
