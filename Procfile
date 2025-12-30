web: gunicorn sdscc.wsgi:application --bind 0.0.0.0:$PORT --timeout 300 --workers 2 --worker-class sync --graceful-timeout 60 --keep-alive 5 --max-requests 500 --max-requests-jitter 50
release: python manage.py migrate --noinput
