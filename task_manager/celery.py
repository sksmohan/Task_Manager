# from __future__ import absolute_import ,unicode_literals
# import os 
# from celery.schedules import crontab
# from celery import Celery
# from django.conf import settings

# os.environ.setdefault("DJANGO_SETTINGS_MODULE",'task_manager.settings')

# app = Celery('task_manager')
# app.conf.enable_utc = False

# app.conf.update(timezone = 'Asia/Kolkata')
# app.config_from_object(settings, namespace='CELERY')

# app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request:{self.request}')

# app.conf.beat_schedule={
#     'send_mail_everyday-at':{
#         'task':'task_pro.task.send_mail_view',  
#         'schedule': crontab(hour=6,minute=30),
#         'args':(1000,)
#     }
# }

# app.conf.beat_schedule ={
#     'send_mail_every-at':{
#         'task':'task_pro.task.pending_notification',
#         'schedule':crontab(hour=9,minute=15),
#         'args':(1000,)
#     }
# }

# app.conf.beat_schedule ={
#     'send_mail_every-at':{
#         'task':'task_pro.task.daily_pending_task_notification',
#         'schedule':crontab(hour=9,minute=30),
#         'args':(1000,) 
#     }
# }





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
for_monthly_duedate = today + timedelta(days=10)
for_weekly_duedate = today + timedelta(days=6)

app.conf.beat_schedule ={
    'every_day_task':{
        'task':'task_pro.task.send_mail_view',
        'schedule': crontab(hour=6,minute=30),
        'args':('Is_daily',today)
    },
    'monthly_task':{
        'task':'task_pro.task.send_mail_view',
        'schedule': crontab(minute=30, hour=8, day_of_month='1'),
        'args':('Is_monthly',for_weekly_duedate)
    },
    'weekly_task':{
        'task':'task_pro.task.send_mail_view',
        'schedule': crontab(minute=30, hour=7, day_of_week="mon"),
        'args':('Is_weekly',for_weekly_duedate)
    },
    'notification_for_dailytask':{
        'task':'task_pro.task.pending_notification',
        'schedule':crontab(hour=9,minute=15),
        'args':(1000,)
    },
    'notification_for_pendingtask':{
        'task':'task_pro.task.daily_pending_task_notification',
        'schedule':crontab(hour=9,minute=30),
        'args':(1000,) 
    }
    
}

