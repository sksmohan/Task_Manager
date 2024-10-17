from django.db import models
from django.contrib.auth.models  import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


# Create your models here.
class Employee(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    department = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username


class Project(models.Model):
    project_name = models.CharField(max_length=100)
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
    assigned_to = models.ForeignKey(Employee,on_delete=models.CASCADE)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    due_date = models.DateField()
    project = models.ForeignKey(Project,on_delete=models.CASCADE,null=True,blank=True)
    status = models.CharField(max_length=100,choices=STATUS_CHOICES,default='Pending')
    message = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.title

@receiver(post_save,sender=Task)
def send_email_on_task_creation(sender,instance,created,**kwargs):
    if created:
        subject = f'New task assigned : {instance.title}'
        message = f'you have been assigned a new task :{instance.description}\n\nDue Date :{instance.due_date}'
        recipient_list = [instance.assigned_to.user.email]

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently = False
        )
