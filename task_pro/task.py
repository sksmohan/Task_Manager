from celery import shared_task
from django.core.mail import send_mail
from task_manager import settings
from .models import Task,Project,CustomUser
from django.utils import timezone
from datetime import timedelta


@shared_task(bind=True)
def testing_view(self,args):
    print("welcome")
    return 'welcome'

@shared_task(bind=True)
def send_mail_view(self,args):
    total_task = Project.objects.filter(Is_daily=True)
    project_info =[]
    today = timezone.now().date()
    for i in total_task:
        project_info.append(i)
    task_filter ={}
    for i in project_info:
        task = Task.objects.filter(project__id=i.id)
        for pro in task:
            if pro.title not in task_filter:
                task_filter[pro.title] = pro
    print(task_filter,len(task_filter))
    for t  in task_filter.values():
        task_creation = Task.objects.create(
            title=t.title,
            description=t.description,
            assigned_to=t.assigned_to,
            created_by=t.created_by,
            due_date=today,
            project=t.project,
            status='Pending'
        )
        task_creation.save()
        print('done')
    return "Task Successfull !"

@shared_task(bind=True)
def send_mail_view_monthly(self,args):
    total_task = Project.objects.filter(Is_monthly=True)
    project_info =[]
    today_for_month = timezone.now().date()
    today = today_for_month + timedelta(days=10)
    for i in total_task:
        project_info.append(i)
    task_filter ={}
    for i in project_info:
        task = Task.objects.filter(project__id=i.id)
        for pro in task:
            if pro.title not in task_filter:
                task_filter[pro.title] = pro
    print(task_filter,len(task_filter))
    for t  in task_filter.values():
        task_creation = Task.objects.create(
            title=t.title,
            description=t.description,
            assigned_to=t.assigned_to,
            created_by=t.created_by,
            due_date=today,
            project=t.project,
            status='Pending'
        )
        task_creation.save()
        print('done')
    return "Task Successfull monthly!"

@shared_task(bind=True)
def send_mail_view_weekly(self,args):
    total_task = Project.objects.filter(Is_weekly=True)
    project_info =[]
    today_for_weekly = timezone.now().date()
    today = today_for_weekly + timedelta(days=6)
    for i in total_task:
        project_info.append(i)
    task_filter ={}
    for i in project_info:
        task = Task.objects.filter(project__id=i.id)
        for pro in task:
            if pro.title not in task_filter:
                task_filter[pro.title] = pro
    print(task_filter,len(task_filter))
    for t  in task_filter.values():
        task_creation = Task.objects.create(
            title=t.title,
            description=t.description,
            assigned_to=t.assigned_to,
            created_by=t.created_by,
            due_date=today,
            project=t.project,
            status='Pending'
        )
        task_creation.save()
        print('done')
    return "Task Successfull weekly!"


@shared_task(bind=True)
def pending_notification(self,args):
    project_retrive = Project.objects.filter(Is_daily=False)
    project_info =[]
    today = timezone.now().date()
    for i in project_retrive:
        project_info.append(i)
    pending_tasks = []
    for i in project_info:
        task = Task.objects.filter(project__id=i.id).filter(status='Pending')
        for task_id in task:
            pending_tasks.append(task_id.id)
    
    today_date = timezone.now().date()
    tomorrow_date = today_date + timedelta(days=1)
    
    for pending_task in pending_tasks:
        p_task = Task.objects.filter(id=pending_task).first()
        if p_task.due_date == tomorrow_date or p_task.due_date < today_date:
            user_id = p_task.assigned_to
            user = CustomUser.objects.get(username=user_id)
            subject = "Task Pending Alert !"
            message = f"Task is to be done by due_date \n Task title : {p_task.title} Due_date : {p_task.due_date}"
            mail_to = user.email

            send_mail(
                subject=subject,
                message=message,
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = [mail_to],
                fail_silently = True
            )
    
    return 'Pending mail has been sent Successfully !'

@shared_task(bind=True)
def daily_pending_task_notification(self,args):
    project_retrive = Project.objects.filter(Is_daily=True)
    project_info =[]
    today = timezone.now().date()
    for i in project_retrive:
        project_info.append(i)
    pending_tasks = []
    for i in project_info:
        task = Task.objects.filter(project__id=i.id).filter(status='Pending')
        for task_id in task:
            pending_tasks.append(task_id.id)
    
    today_date = timezone.now().date()
    tomorrow_date = today_date + timedelta(days=1)
    
    for pending_task in pending_tasks:
        p_task = Task.objects.filter(id=pending_task).first()
        if p_task.due_date < today_date:
            user_id = p_task.assigned_to
            user = CustomUser.objects.get(username=user_id)
            subject = "Daily_Task Pending Alert !"
            message = f"Task is to be done by due_date \n Task title : {p_task.title} Due_date : {p_task.due_date}"
            mail_to = user.email

            send_mail(
                subject=subject,
                message=message,
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = [mail_to],
                fail_silently = True
            )
    
    return 'Daily_task Pending mail has been sent Successfully !'
