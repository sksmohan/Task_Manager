from django.db import models
from django.contrib.auth.models  import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    choose = (
        ('Accounts-AR','Accounts-AR'),
        ('Accounts-Ap','Accounts-Ap'),
        ('Accounts-MIS','Accounts-MIS'),
        ('Accounts Manager','Accounts Manager'),
        ('MIS','MIS'),
        ('HR','HR'),
        ('Sales Admin','Sales Admin'),
        ('Zonals Managers','Zonals Managers'),
        ('Branch Manager','Branch Manager'),
        ('Employee','Employee'),
        ('IT','IT'),
        ('Sales','Sales'),
        ('MM Management','MM Management')
    )
    email = models.EmailField(blank=False, null=False)
    department = models.CharField(choices=choose,max_length=100,default='Sales')
    head = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='images/',blank=True,null=True)

class Project(models.Model):
    project_name = models.CharField(max_length=100)
    Is_daily = models.BooleanField(default=False)
    Is_weekly = models.BooleanField(default=False)
    Is_monthly = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return self.project_name
class Task(models.Model):
    STATUS_CHOICES  = (
        ('Pending','Pending'),
        ('In progress','In progress'),
        ('Completed','Completed'),
        ('Stuck','Stuck'))

    task_created_at = models.DateTimeField(auto_now_add=True)
    title= models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name ="assigned_to")
    created_by = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name="created_by")
    due_date = models.DateField()
    project = models.ForeignKey(Project,on_delete=models.CASCADE,null=True,blank=True)
    status = models.CharField(max_length=100,choices=STATUS_CHOICES,default='Pending')
    message = models.TextField(null=True,blank=True)
    audio = models.FileField(upload_to='audio/',null=True, blank=True)

    task_depended_on = models.IntegerField(null=True,blank=True)
    struck_time_start_at = models.DateTimeField(max_length=100,null=True,blank=True)
    stuck_time_end_at = models.DateTimeField(null=True,blank=True)
    incomplete = models.BooleanField(default=False)

    waiting_for = models.IntegerField(null=True,blank=True)
    waiting_for_username = models.CharField(max_length=100,null=True,blank=True)
    waiting_time_start_at = models.DateTimeField(null=True,blank=True)         
    task_completed_at = models.DateTimeField(null=True,blank=True)
    is_late  = models.BooleanField(default=False)
    including_sunday = models.BooleanField(default=False)


    def __str__(self):
        return self.title

class multi_document(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='document')
    document = models.FileField(upload_to='documents/',null=True,blank=True)

    def __str__(self):
        return self.document.url if self.document else "No Document"