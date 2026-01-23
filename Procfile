release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py clear_featured_images
web: gunicorn only_studies.wsgi
