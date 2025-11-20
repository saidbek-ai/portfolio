from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from portfolio.redis.constants import CLEAN_UP_INTERVAL


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')

app = Celery('portfolio')

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    f'clean-offline-users-every-{CLEAN_UP_INTERVAL}-seconds': {
        'task': 'users.tasks.clean_offline_users',
        'schedule': CLEAN_UP_INTERVAL,
    },
}