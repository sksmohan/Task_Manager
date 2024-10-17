from celery import shared_task
from django.core.mail import send_mail
from task_manager import settings



@shared_task(bind=True)
def test_func(self):
    for i in range(10):
        print(i)
    return "Done_done"

@shared_task(bind=True)
def send_mail_view(self):
    subject = "This is your title"
    message = 'task has been assigned to you'
    mail_to = 'isganeshv@gmail.com'
    send_mail(
        subject=subject,
        message = message,
        from_email = settings.EMAIL_HOST_USER,
        recipient_list = [mail_to],
        fail_silently = True

    )
    return "Task Successfull !"
