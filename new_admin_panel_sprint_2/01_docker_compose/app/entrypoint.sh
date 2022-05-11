#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
# fill our new static folder for nginx and migrate
python manage.py collectstatic --no-input --clear
python manage.py migrate
# create superuser
if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL || true
fi
gunicorn config.wsgi:application --bind 0.0.0.0:8000

exec "$@"
