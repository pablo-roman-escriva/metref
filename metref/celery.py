# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery,shared_task
from django.conf import settings
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import subprocess
from django.apps import apps

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metref.settings')

app = Celery('metref')  # Replace 'your_project' with your project's name.

# Configure Celery using settings from Django settings.py.

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered Django app configs.
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

app.conf.broker_connection_retry_on_startup = True

logger = get_task_logger(__name__)

app.conf.beat_schedule = {
    # Executes every Monday morning at 7:30 a.m.
    'remove-temp-every-day': {
        'task': 'metref.celery.empty_temp_folder_studies',
        'schedule': crontab(hour=0, minute=15),
    },
    'update-db-every-two-months': {
        'task': 'metref.celery.update_db',
        'schedule': crontab(hour=1, minute=0, day_of_week=1, month_of_year="10,12,2,4,6,8"),
    },
}

@shared_task
def empty_temp_folder_studies():
    os.system('rm -rf temp/*')

@shared_task
def update_db():
    os.system("utils/update_genomes.py")
