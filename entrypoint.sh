#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE="config.settings"

echo "=== [1/3] Running Django migrations ==="
python manage.py migrate --noinput

echo "=== [2/3] Ensuring superuser exists ==="
python manage.py create_admin

echo "=== [3/3] Checking Cairo student housing initial data ==="
python -c "
import django
django.setup()
from apps.properties.models import Property
if Property.objects.count() == 0:
    from django.core.management import call_command
    print('Seeding initial Cairo student housing data...')
    call_command('seed_cairo_student_data')
else:
    print(f'Database already populated with {Property.objects.count()} student properties.')
"

echo "=== Cairo Student Housing server ready ==="
exec "$@"
