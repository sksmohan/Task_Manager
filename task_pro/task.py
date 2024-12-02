from celery import shared_task
from django.core.mail import send_mail
from task_manager import settings
from .models import Task,Project
from django.utils import timezone


@shared_task(bind=True)
def test_func(self):
    for i in range(10):
        print(i)
    return "Done_done"

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
    # subject = "This is your title"
    # message = 'task has been assigned to you'
    # mail_to = 'isganeshv@gmail.com'
    # send_mail(
    #     subject=subject,
    #     message = message,
    #     from_email = settings.EMAIL_HOST_USER,
    #     recipient_list = [mail_to],
    #     fail_silently = True
    # )
    return "Task Successfull !"
