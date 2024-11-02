from __future__ import absolute_import ,unicode_literals
import os 
from celery.schedules import crontab
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE",'task_manager.settings')

app = Celery('task_manager')
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kolkata')
app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request:{self.request}')

app.conf.beat_schedule={
    'send_mail_everyday-at':{
        'task':'task_pro.task.send_mail_view',
        'schedule': crontab(hour=10,minute=16),
        'args':(1000,)
    }
}