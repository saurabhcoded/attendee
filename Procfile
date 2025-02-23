web: sh -c "python manage.py collectstatic --no-input && gunicorn attendee.wsgi"
worker: celery -A attendee worker -l info