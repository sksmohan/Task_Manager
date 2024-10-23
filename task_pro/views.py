from .task import test_func ,send_mail_view
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from .models import Task,Project,CustomUser
from .forms import taskform ,loginForm,projectfilterform,CustomUserForm,Taskcreation_form,project_form
from datetime import datetime ,timedelta
from django.utils import timezone
from django.db.models import Q
from django_celery_beat.models import PeriodicTask, IntervalSchedule,CrontabSchedule

from django.core.mail import send_mail
from django.conf import settings
# Create your views here.

@login_required
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

    
    department = Task.objects.filter(assigned_to=request.user.id).first()
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

@login_required
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

    department = Task.objects.filter(assigned_to=request.user.id).first()

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

    department = Task.objects.filter(assigned_to=request.user.id).first()
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

@login_required
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

@login_required
def filter_search(request):
    department = Task.objects.filter(assigned_to=request.user.id).first()
    if request.method =="POST":
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        project = request.POST.get('project')
        project_form = projectfilterform(request.POST)
        filter_task = Task.objects.filter(assigned_to=request.user.id,due_date__gte=from_date,due_date__lte=to_date,project=project).order_by('due_date')
        return render(request,"filter.html",context={'department':department,'filter_task':filter_task,'project_form':project_form,'from_date':from_date,'to_date':to_date})
    project_form = projectfilterform()
    return render(request,"filter.html",context={'department':department,'project_form':project_form})

@login_required
def over_due(request):
    today = timezone.now().date()
    over_due_tasks = Task.objects.filter(assigned_to=request.user.id,due_date__lt=today).filter(Q(status="In progress") | Q(status="Pending")).order_by('due_date')
    return render(request,'overdue_task.html',{"overdue_task":over_due_tasks})

@login_required
def add_user(request):
    if request.method =='POST':
        form = CustomUserForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        else:
            messages.error(request,'error')
            return render(request,'add_user.html',{'form':form})
    form =CustomUserForm()
    return render(request,'add_user.html',{'form':form})

@login_required
def Team_mem(request):
    members = CustomUser.objects.filter(department=request.user.department).exclude(username=request.user).order_by('username')
    mem_dict ={}
    for i in members:
        pending =0
        in_progress=0
        mem_dict[i.username]={'pending':pending,'in_progress':in_progress,'id':i.id}
        mem = Task.objects.filter(assigned_to=i)
        for k in mem:
            if k.status =="In progress":
                in_prin_progressogess+=1
            else:
                pending+=1
        mem_dict[i.username]['pending']=pending
        mem_dict[i.username]["in_progress"]=in_progress
    return render(request,'team_mem.html',{"mem_dict":mem_dict})

@login_required
def profile_update(request,pk):
    current_url = request.build_absolute_uri()
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

    today_task = Task.objects.filter(assigned_to=pk,due_date=today)
    yesterday = Task.objects.filter(assigned_to =pk,due_date=yesterday)
    this_week = Task.objects.filter(assigned_to=pk,due_date__gte=start_of_week,due_date__lte=end_of_week)
    last_week = Task.objects.filter(assigned_to=pk,due_date__gte=start_of_lastweek,due_date__lte=end_of_lastweek)
    this_month = Task.objects.filter(assigned_to=pk,due_date__gte=start_of_month,due_date__lte=end_of_month)
    last_month = Task.objects.filter(assigned_to=pk,due_date__lt=start_of_lastweek)
    total_count = len(today_task)+len(yesterday)+len(this_week)+len(last_week)+len(this_month)+len(last_month)+len(last_month)

    department = Task.objects.filter(assigned_to=request.user.id).first()
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
    return render(request,"profile_update.html",context)

@login_required
def profile_task_update(request,pk):
    task = Task.objects.get(id=pk)
    assigned_for = task.assigned_to.id
    if request.method == "POST":
        form = taskform(data=request.POST,instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        else:
            print('Form is not valid:', form.errors)
    form = taskform(instance=task)
    return render(request,'profile_task_update.html',{'tasks':task,'form':form,'id':assigned_for,'task_id':task.id})

@login_required
def delete_task(request,pk):
    task = Task.objects.get(id=pk)
    user_id = task.assigned_to.id
    task.delete()
    return redirect('profile_update',user_id)   

# pradeep bits consultancy

@login_required
def new_task_creation(request):
    members = CustomUser.objects.filter(department=request.user.department).exclude(id=request.user.id).order_by("id")
    if request.method == 'POST':
        assign11 = request.POST.get('assigned_to')
        assign = CustomUser.objects.get(username=assign11)
        form = Taskcreation_form(data=request.POST)
        if form.is_valid():
            task_instance = form.save(commit=False)
            task_instance.assigned_to= assign
            task_instance.save()
            messages.success(request,"Your Task has been created successfully!")
            return redirect('new_task_creation')
        return render(request,'new_task.html',{"form":form,"members":members})
    form = Taskcreation_form()
    return render(request,'new_task.html',{"form":form,"members":members})

def project_creation(request):
    if request.method == "POST":
        form = project_form(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your project has been created successfully!")
            return redirect('project_creation')
        return render(request,"project_creation.html",{'form':form})
    form = project_form()
    return render(request,'project_creation.html',{'form':form})

def login_view(request):
    if request.method == "POST":
        form = loginForm(data=request.POST)
        id = request.POST.get('username')
        passw = request.POST.get('password')
        if not id or not passw:
            messages.error(request,"Username and pasword required")
            return render(request, 'login.html', {'form': form})
        if form.is_valid():
            user_name = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=user_name,password=password)
            if user is not None:
                login(request,user)
                return redirect('dashboard')
            else:
                error=1
                messages.error(request, "Invalid username or password.")
                return render(request,'login.html',{'form':form,'error':error})
    form= loginForm()
    return render(request,'login.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect('login')

def admin_login(request):
    pass


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

def mailattime(request):
    schedule,created=CrontabSchedule.objects.get_or_create(hour=16,minute=59)
    task = PeriodicTask.objects.create(crontab=schedule,name="mail_task"+"1",task='task_pro.task.send_mail_view')
    return HttpResponse("success")
