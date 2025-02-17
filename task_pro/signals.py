from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime
import requests
import json

@receiver(post_save,sender=Task)
def incomplete_change(sender,instance,created,**kwargs):
    post_save.disconnect(incomplete_change,sender=Task) 
    try:
        status = instance.status
        if status == "Completed":
            task = Task.objects.filter(id=instance.id).first()
            if instance.incomplete:
                task.incomplete =False
                task.task_completed_at = datetime.now()
                current_date = datetime.now().date()
                due_date = task.due_date
                task.is_late = current_date > due_date
                
                waiting_user = Task.objects.filter(id=instance.waiting_for).first()
                print(waiting_user)
                waiting_user.stuck_time_end_at = datetime.now()
                waiting_user.save()
                task.save()
                return
            else:
                task.task_completed_at = datetime.now()
                current_date = datetime.now().date()
                due_date = task.due_date
                task.is_late = current_date > due_date
                task.save()
                return
        if status == "Stuck":
            pk = instance.task_depended_on
            task = Task.objects.filter(id=pk).first()
            if task:
                task.incomplete = True if status == "Stuck" else False
                task.waiting_for = instance.id
                task.waiting_for_username = instance.assigned_to.username
                task.waiting_time_start_at = datetime.now()
                task.save()
                return
            else:
                print("Task not found with ID:", instance.task_depended_on,pk)
                return
    finally:
        post_save.connect(incomplete_change,sender=Task)


@receiver(post_save,sender=Task)
def send_email_on_task_creation(sender,instance,created,**kwargs):
    if created:
        url = 'https://api.wacto.app/api/v1.0/messages/send-template/919840443294'
        header ={
            "Content-Type":"application/json",
            "Authorization":"Bearer kMfPR5XjEkSoHX4QDoeBoQ"
        }
        payload ={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": instance.assigned_to.phone_number,
            "type": "template",
            "template": {
                "name": "task_creation",
                "language": {
                "code": "en"
                },
                "components": [
                {
                    "type": "body",
                    "parameters": [
                    {
                        "type": "text",
                        "text": str(instance.assigned_to)
                    },
                    {
                        "type": "text",
                        "text": str(instance.title)
                    },
                    {
                        "type": "text",
                        "text": str(instance.created_by)
                    },
                    {
                        "type": "text",
                        "text": str(instance.project)
                    },
                    {
                        "type": "text",
                        "text": str(instance.due_date)
                    }
                    ]
                }
                ]
            }
        }
        print(instance.assigned_to.phone_number)
        response1 = requests.post(url,data=json.dumps(payload),headers=header)
