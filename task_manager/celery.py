from __future__ import absolute_import ,unicode_literals
import os 
from celery.schedules import crontab
from celery import Celery
from django.conf import settings
from datetime import datetime ,timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE",'task_manager.settings')

app = Celery('task_manager')
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kolkata')
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request:{self.request}')

today = timezone.now().date()
for_monthly_duedate = today + timedelta(days=11)
for_weekly_duedate = today + timedelta(days=7)
today_date = today + timedelta(days=1)

app.conf.beat_schedule ={
    'for_testing':{
        'task':'task_pro.task.testing_view',
        'schedule':crontab(hour=6,minute=29),
        'args':(1000,)
    },
    'every_day_task':{
        'task':'task_pro.task.send_mail_view',
        'schedule': crontab(hour=6,minute=30),
        'args':(1000,)
    },
    'monthly_task':{
        'task':'task_pro.task.send_mail_view_monthly',
        'schedule': crontab(minute=15, hour=7, day_of_month='7'),
        'args':(1000,)
    },
    'weekly_task':{
        'task':'task_pro.task.send_mail_view_weekly',
        'schedule': crontab(minute=30, hour=7, day_of_week="tue"),
        'args':(1000,)
    },
    'notification_for_dailytask':{
        'task':'task_pro.task.pending_notification',
        'schedule':crontab(hour=9,minute=30),
        'args':(1000,)
    },
    'notification_for_pendingtask':{
        'task':'task_pro.task.daily_pending_task_notification',
        'schedule':crontab(hour=9,minute=45),
        'args':(1000,)
    }
}