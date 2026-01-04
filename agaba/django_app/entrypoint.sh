#!/bin/sh
set -e

max_tries="${DJANGO_DB_WAIT_MAX_TRIES:-15}"
sleep_seconds="${DJANGO_DB_WAIT_SLEEP:-2}"
try=1

while [ "$try" -le "$max_tries" ]; do
  if python manage.py migrate --noinput; then
    break
  fi
  echo "Database is not ready (attempt $try/$max_tries). Retrying in $sleep_seconds seconds..." >&2
  try=$((try + 1))
  sleep "$sleep_seconds"
done

if [ "$try" -gt "$max_tries" ]; then
  echo "Database is not ready after $max_tries attempts." >&2
  exit 1
fi

python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

def is_enabled():
    value = os.environ.get("DJANGO_CREATE_SUPERUSER")
    if value is None:
        return os.environ.get("DEBUG", "0").lower() in ("1", "true", "yes", "on")
    return value.lower() in ("1", "true", "yes", "on")

if not is_enabled():
    raise SystemExit(0)

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin")

User = get_user_model()
user = User.objects.filter(username=username).first()
if user:
    print(f"Superuser '{username}' already exists, skipping.")
    raise SystemExit(0)

user = User.objects.create_user(username=username, password=password)
user.is_staff = True
user.is_superuser = True
if hasattr(user, "role"):
    user.role = "admin"
user.save()
print(f"Superuser '{username}' created.")
PY

exec "$@"
