#!/bin/bash

# Загрузка переменных окружения из .env файла
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Файл .env не найден в директории $SCRIPT_DIR"
    exit 1
fi

echo "Скрипт запущен из директории: $SCRIPT_DIR"

# Функция для завершения активных сессий базы данных
terminate_sessions() {
    sudo -u postgres psql -c "
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '$POSTGRES_DB';
    "
}

# Функция для создания базы данных и пользователя
create_db_and_user() {
    echo "Создание базы данных $POSTGRES_DB и пользователя $POSTGRES_USER..."

    # Завершаем активные сессии, если база данных существует
    terminate_sessions

    # Подключаемся к PostgreSQL и выполняем команды
    sudo -u postgres psql <<EOF
-- Удаляем базу данных, если она существует
DROP DATABASE IF EXISTS $POSTGRES_DB;

-- Удаляем пользователя, если он существует
DROP USER IF EXISTS $POSTGRES_USER;

-- Создаем нового пользователя и задаем пароль
CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';

-- Создаем новую базу данных и назначаем владельца
CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;

-- Предоставляем все права на базу данных пользователю
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
EOF

    echo "База данных и пользователь успешно созданы."
}

# Функция для предоставления прав на таблицы
grant_table_privileges() {
    echo "Предоставление прав на таблицы пользователю $POSTGRES_USER..."

    sudo -u postgres psql -d $POSTGRES_DB <<EOF
-- Предоставляем права на все таблицы в схеме public
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $POSTGRES_USER;

-- Предоставляем права на все последовательности в схеме public
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $POSTGRES_USER;

-- Автоматическое предоставление прав на новые таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $POSTGRES_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO $POSTGRES_USER;
EOF

    echo "Права на таблицы успешно предоставлены."
}

# Функция для удаления всех миграций
delete_all_migrations() {
    echo "Удаление всех существующих миграций..."

    # Находим все файлы миграций в папках migrations и удаляем их
    find "$SCRIPT_DIR/django_app" -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find "$SCRIPT_DIR/django_app" -path "*/migrations/*.pyc" -delete

    echo "Все миграции успешно удалены."
}

# Основной блок выполнения скрипта
echo "Начинаем настройку базы данных и пользователя..."
create_db_and_user
grant_table_privileges
echo "Настройка базы данных завершена."

# Удаление всех миграций
delete_all_migrations

# Генерация новых миграций Django
echo "Генерация новых миграций Django..."
python3 $SCRIPT_DIR/django_app/manage.py makemigrations

# Применение миграций Django
echo "Применение миграций Django..."
python3 $SCRIPT_DIR/django_app/manage.py migrate

# Создание суперпользователя Django
echo "Создание суперпользователя Django..."
echo "from django.contrib.auth import get_user_model;
User = get_user_model();
User.objects.create_superuser('admin', 'admin@example.com', '$SUPER_USER_PASSWORD')" |
python3 $SCRIPT_DIR/django_app/manage.py shell

echo "Скрипт выполнен успешно."