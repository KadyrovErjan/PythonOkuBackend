import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

try:
    from celery import Celery
except Exception:
    app = None
else:
    app = Celery('mysite')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
