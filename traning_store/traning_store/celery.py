import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traning_store.settings')

app = Celery('traning_store',
             broker_connection_retry_on_startup=settings.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP,
             broker=settings.CELERY_BROKER_URL,
             backend=settings.CELERY_RESULT_BACKEND
             )

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    worker_pool_restarts=True,
)