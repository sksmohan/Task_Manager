from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime

@receiver(post_save,sender=Task)
def incomplete_change(sender,instance,created,**kwargs):
    post_save.disconnect(incomplete_change,sender=Task) 
    try:
        status = instance.status
        if status == "Completed":
            task = Task.objects.filter(id=instance.id).first()
            if instance.incomplete:
                task.incomplete =False
                task_completed_time = datetime.now()
                format_completed_time = task_completed_time.strftime("%Y-%m-%d %H:%M:%S")
                task.task_completed_at = task_completed_time
                

                waiting_user = Task.objects.filter(id=instance.waiting_for).first()
                print(waiting_user)
                waiting_user.stuck_time_end_at = format_completed_time
                waiting_user.save()
                task.save()
                return
            else:
                task_completed_time = datetime.now()
                format_completed_time = task_completed_time.strftime("%Y-%m-%d %H:%M:%S")
                task.task_completed_at = task_completed_time
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
        subject = f'New task assigned : {instance.title}'
        message = f'you have been assigned a new task :{instance.description}\n\nDue Date :{instance.due_date}'
        recipient_list = [instance.assigned_to.email]

        print(subject,message,recipient_list)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently = False
        )
