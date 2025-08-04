#!/usr/bin/env bash
set -e

echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h db -p 5432 -U "$DB_USER"; do
  sleep 1
done
echo "✅ PostgreSQL is ready"

python manage.py migrate --no-input

python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="${DJANGO_SUPERUSER_USERNAME}").exists():
    User.objects.create_superuser(
        username="${DJANGO_SUPERUSER_USERNAME}",
        password="${DJANGO_SUPERUSER_PASSWORD}"
    )
EOF

python manage.py runserver 0.0.0.0:8000