# AGABA Backend

AGABA - backend платформы для размещения товаров, работы с компаниями и заказами (покупка/лизинг).
Проект построен на Django/DRF и предоставляет REST API, а также часть серверных шаблонов.

## Что внутри
- account - пользователи, роли, компании.
- products - каталог, категории, атрибуты, документы/фото, отзывы, избранное, сравнение.
- order - заказы и стадии, доп. опции, назначение менеджера.
- balance - баланс, пополнения/выводы, операции, PDF счетов.
- messenger - сообщения и чаты.
- api - REST API, сериализаторы и вьюсеты.
- django_app - настройки, ASGI/WSGI, Kafka-обвязка.

## Стек
- Django 5.1 + DRF
- JWT (SimpleJWT) + Djoser
- Channels (WebSocket)
- PostgreSQL (локалка SQLite)
- Redis (кеш/OTP)
- MinIO (S3-хранилище)
- drf-yasg (Swagger/Redoc)
- Kafka (опционально для событий)


## Документация API
- Swagger: `/api/v1/swagger/`
- Redoc: `/api/v1/redoc/`

## Переменные окружения
Минимальный набор для локальной разработки (SQLite по умолчанию):

```env
DEBUG=1
SECRET_KEY=dev-secret
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1
```

Для PostgreSQL:

```env
POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=agaba
POSTGRES_USER=agaba
POSTGRES_PASSWORD=agaba
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Дополнительно/опционально:
- Redis кеш: настраивается в `agaba/django_app/django_app/settings.py` (по умолчанию `redis://127.0.0.1:6380/1`).
- MinIO/S3:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_STORAGE_BUCKET_NAME`
- Kafka:
  - `KAFKA_ENABLED=1`
  - `KAFKA_BOOTSTRAP_SERVERS=localhost:9092`
  - `KAFKA_OPERATION_TOPIC=operations`
- DaData (подсказки по компаниям): `TOKEN_DADATA`

## Docker
Есть окружения:
- `agaba/infra/stage/docker-compose.yml`
- `agaba/infra/prod/docker-compose.yml`

Запуск (пример для stage):

```bash
cd agaba/infra/stage
docker compose up -d --build
```

При старте контейнера создается суперпользователь для админки (если еще нет):
- логин: `admin`
- пароль: `admin`

Можно переопределить:
- `DJANGO_CREATE_SUPERUSER=0|1`
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_PASSWORD`

## Тесты

```bash
cd agaba/django_app
python manage.py test
```

## Полезное
- `agaba/django_app/db_dump.json` - дамп тестовых данных.
- `agaba/django_app/requirements.txt` - используется Dockerfile.
- `agaba/requirements.txt` - полный список зависимостей для локальной разработки.
