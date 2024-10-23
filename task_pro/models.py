from django.db import models
from django.contrib.auth.models  import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    choose = (
        ('IT','IT'),
        ('Sales','Sales')
    )
    email = models.EmailField(blank=False, null=False)
    department = models.CharField(choices=choose,max_length=100,default='Sales')
    head = models.BooleanField(default=False)


class Project(models.Model):
    project_name = models.CharField(max_length=100)
    Is_daily = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return self.project_name

class Task(models.Model):
    STATUS_CHOICES  = (
        ('Pending','Pending'),
        ('In progress','In progress'),
        ('Completed','Completed'))
    title= models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name ="assigned_to")
    created_by = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name="created_by")
    due_date = models.DateField()
    project = models.ForeignKey(Project,on_delete=models.CASCADE,null=True,blank=True)
    status = models.CharField(max_length=100,choices=STATUS_CHOICES,default='Pending')
    message = models.TextField(null=True,blank=True)
    audio = models.FileField(upload_to='voice_messages/',null=True,blank=True)

    def __str__(self):
        return self.title

@receiver(post_save,sender=Task)
def send_email_on_task_creation(sender,instance,created,**kwargs):
    if created:
        subject = f'New task assigned : {instance.title}'
        message = f'you have been assigned a new task :{instance.description}\n\nDue Date :{instance.due_date}'
        recipient_list = [instance.assigned_to.email]

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently = False
        )
