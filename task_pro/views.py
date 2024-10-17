from .task import test_func ,send_mail_view
from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from .models import Task,Employee,Project
from .forms import taskform ,loginForm,projectfilterform
from datetime import datetime ,timedelta
from django.utils import timezone
from django.db.models import Q
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from django.core.mail import send_mail
from django.conf import settings
# Create your views here.
def dashboard(request):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    end_of_lastweek = start_of_week - timedelta(days=1)
    start_of_lastweek = end_of_lastweek - timedelta(days=6)
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    end_of_lastmonth = start_of_month - timedelta(days=1)
    start_of_lastmonth = end_of_lastmonth - timedelta(days=29)

    today_task = Task.objects.filter(assigned_to=request.user.id,due_date=today)
    yesterday = Task.objects.filter(assigned_to =request.user.id,due_date=yesterday)
    this_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_week,due_date__lte=end_of_week)
    last_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_lastweek,due_date__lte=end_of_lastweek)
    this_month = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_month,due_date__lte=end_of_month)
    last_month = Task.objects.filter(assigned_to=request.user.id,due_date__lt=start_of_lastweek)
    total_count = len(today_task)+len(yesterday)+len(this_week)+len(last_week)+len(this_month)+len(last_month)+len(last_month)

    
    department = Employee.objects.filter(user=request.user.id).first()
    context ={
        'today_task':today_task,
        'yesterday':yesterday,
        'this_week':this_week,
        'last_week':last_week,
        'this_month':this_month,
        'last_month':last_month,
        'department':department,
        'total_count':total_count
    }

    return render(request,'dashboard.html',context)


def specific_task(request,name):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    end_of_lastweek = start_of_week - timedelta(days=1)
    start_of_lastweek = end_of_lastweek - timedelta(days=6)
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    end_of_lastmonth = start_of_month - timedelta(days=1)
    start_of_lastmonth = end_of_lastmonth - timedelta(days=29)

    department = Employee.objects.filter(user=request.user.id).first()

    if name =="Pending" or name =="In progress" or name =="Completed":
        today_task = Task.objects.filter(assigned_to=request.user.id,due_date=today,status = name)
        yesterday = Task.objects.filter(assigned_to =request.user.id,due_date=yesterday,status = name)
        this_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_week,due_date__lte=end_of_week,status = name)
        last_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_lastweek,due_date__lte=end_of_lastweek,status = name)
        this_month = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_month,due_date__lte=end_of_month,status = name)
        last_month = Task.objects.filter(assigned_to=request.user.id,due_date__lt=start_of_lastweek,status = name)
        total_count = len(today_task)+len(yesterday)+len(this_week)+len(last_week)+len(this_month)+len(last_month)+len(last_month)
    else:
        today_task = Task.objects.filter(assigned_to=request.user.id,due_date=today)
        yesterday = Task.objects.filter(assigned_to =request.user.id,due_date=yesterday)
        this_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_week,due_date__lte=end_of_week)
        last_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_lastweek,due_date__lte=end_of_lastweek)
        this_month = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_month,due_date__lte=end_of_month)
        last_month = Task.objects.filter(assigned_to=request.user.id,due_date__lt=start_of_lastweek)
        total_count = len(today_task)+len(yesterday)+len(this_week)+len(last_week)+len(this_month)+len(last_month)+len(last_month)

    department = Employee.objects.filter(user=request.user.id).first()
    context ={
        'today_task':today_task,
        'yesterday':yesterday,
        'this_week':this_week,
        'last_week':last_week,
        'this_month':this_month,
        'last_month':last_month,
        'department':department,
        'total_count':total_count
    }

    return render(request,'dashboard.html',context)


def update_task(request,pk):
    task = Task.objects.get(assigned_to=request.user.id,id=pk)
    if request.method == "POST":
        form = taskform(data=request.POST,instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        else:
            print('Form is not valid:', form.errors)
    form = taskform(instance=task)
    return render(request,'update_tasks.html',{'tasks':task,'form':form})

def filter_search(request):
    department = Employee.objects.filter(user=request.user.id).first()
    if request.method =="POST":
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        project = request.POST.get('project')
        project_form = projectfilterform(request.POST)
        filter_task = Task.objects.filter(assigned_to=request.user.id,due_date__gte=from_date,due_date__lte=to_date,project=project).order_by('due_date')
        return render(request,"filter.html",context={'department':department,'filter_task':filter_task,'project_form':project_form,'from_date':from_date,'to_date':to_date})
    project_form = projectfilterform()
    return render(request,"filter.html",context={'department':department,'project_form':project_form})

def over_due(request):
    today = timezone.now().date()
    over_due_tasks = Task.objects.filter(assigned_to=request.user.id,due_date__lt=today).filter(Q(status="In progress") | Q(status="Pending")).order_by('due_date')
    return render(request,'overdue_task.html',{"overdue_task":over_due_tasks})

def login_view(request):
    if request.method == "POST":
        form = loginForm(data=request.POST)
        if form.is_valid():
            user_name = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(user_name,"and",password)
            user = authenticate(username=user_name,password=password)
            if user is not None:
                login(request,user)
                return redirect('dashboard')
            else:
                error=1
                return render(request,'login.html',{'form':form,'error':error})
    form= loginForm()
    return render(request,'login.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect('login')

def admin_login(request):
    pass
    # if request.method == "POST":
    #     admin_logi_form = AuthenticationForm(data=request.POST)
    #     admin_login_form.is_valid():
    #         username = admin_login_form.cleaned_data.get('username')
    #         password = admin_login_form.cleaned_data.get('password')
    #         user = authenticate(username=username,password=password)
    #         if user is not Nne:
    #             login()
    # admin_login_form = AuthenticationForm()
    # return render('admin_login.html')

def test(request):
    test_func.delay()
    return HttpResponse("done")

def schedule_task(request):
    interval,_ = IntervalSchedule.objects.get_or_create(
        every = 30,
        period = IntervalSchedule.SECONDS,
    )

    PeriodicTask.objects.create(
        interval = interval,
        name = "my-schedule",
        task = "task_pro.task.test_func",
        # args = json.dumps(["Arg1","Args2"])
        # one_off = True
    )

    return "Task Scheduled !"


def send_mail_(request):
    send_mail_view.delay()
    return HttpResponse('mail has been sent to your email')



