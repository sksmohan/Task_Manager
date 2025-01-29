from .task import send_mail_view
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, datetime, time

from datetime import datetime
from django.shortcuts import get_object_or_404
from django.shortcuts import render , redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from .models import Task,Project,CustomUser,multi_document
from .forms import taskform ,loginForm,projectfilterform,CustomUserForm,Taskcreation_form,project_form
from datetime import datetime ,timedelta
from django.utils import timezone
from django.db.models import Q
from django_celery_beat.models import PeriodicTask, IntervalSchedule,CrontabSchedule

from django.core.mail import send_mail
from django.conf import settings
# Create your views here.


def filter_of_charts(request):
    if request.method == "POST":
        from_date_ = request.POST.get('from_date')
        to_date_ = request.POST.get('to_date')

        from_date = datetime.strptime(from_date_, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_, '%Y-%m-%d').date()
        from_date_2_with_time_and_seconds = datetime.combine(from_date, time(1, 0, 30))
        to_date_2_with_11_55_pm = datetime.combine(to_date, time(23, 55))

        total_task_retrival = Task.objects.filter(assigned_to=request.user.id,task_created_at__gte=from_date_2_with_time_and_seconds,task_created_at__lte=to_date_2_with_11_55_pm).count()
        completed_tasks = Task.objects.filter(assigned_to=request.user.id,incomplete=False,task_created_at__gte=from_date_2_with_time_and_seconds,task_created_at__lte=to_date_2_with_11_55_pm )
        count_of_completed = 0
        count_completedtask_by_duedate = 0
        count_completedtask_after_duedate = 0
        for task in completed_tasks:
            if task.task_completed_at is not None:
                duedate = task.due_date
                str_completedate = str(task.task_completed_at).split(' ')[0]
                completedate = datetime.strptime(str_completedate,"%Y-%m-%d").date()
                if duedate < completedate:
                    count_of_completed+=1
                    count_completedtask_after_duedate+=1
                else:
                    count_of_completed+=1
                    count_completedtask_by_duedate+=1
                print(duedate,'duedate')
                print(completedate,'completed')
                print(duedate < completedate)
        average_of_task_lead =0
        # print(cal_completedtask_by_duedate,"cal_completedtask_by_duedate-------------")
        print(count_of_completed,'count_of_completed')
        cal_completedtask_by_duedate = 0
        cal_completedtask_after_duedate = 0

        if count_completedtask_after_duedate:
            cal_completedtask_after_duedate = int((count_completedtask_after_duedate/total_task_retrival)*100)
        if count_completedtask_by_duedate:
            cal_completedtask_by_duedate = int((count_completedtask_by_duedate/total_task_retrival)*100)
        if count_of_completed:
            average_of_task_lead = int((count_of_completed/total_task_retrival)*100)
        command_for_task_ = None
        color_of_bar = None
        if average_of_task_lead >= 90:
            command_for_task_ = '😀 Very Good!'
            color_of_bar ="#2fc30d"
            color_of_bar ="8ff090"
        elif average_of_task_lead >= 50:
            command_for_task_ ='🙂 ok'
            color_of_bar ="#dfe159"
        elif average_of_task_lead >=20:
            command_for_task_ ="🙁 Consider"
            color_of_bar ="#f3c349"
        else:
            command_for_task_ = "😢 bad"
            color_of_bar ="#ee720d"

        def average_calculation(start,end,project_name,from_date,to_date):
            today = timezone.now().date()
            total_tasks = None
            completed_tasks = None
            if start == 0 and end == 0:
                total_tasks = Task.objects.filter(assigned_to=request.user.id,project__project_name=project_name,task_created_at__gte=from_date,task_created_at__lte=to_date).count()
                completed_tasks = Task.objects.filter(assigned_to=request.user.id,project__project_name=project_name,task_created_at__gte=from_date,task_created_at__lte=to_date)
            elif end == 0 and project_name == 0:
                total_tasks = Task.objects.filter(due_date=start,assigned_to=request.user.id).count()
                completed_tasks = Task.objects.filter(assigned_to=request.user.id,due_date=start,incomplete=False)
            else:
                total_tasks = Task.objects.filter(assigned_to=request.user.id,due_date__lte=end,due_date__gte=start).count()
                completed_tasks = Task.objects.filter(assigned_to=request.user.id,due_date__lte=end,due_date__gte=start)

            count_of_completed = 0
            for task in completed_tasks:
                if task.task_completed_at is not None:
                    count_of_completed+=1
            average_of_task =None
            if count_of_completed:
                average_of_task = int((count_of_completed/total_tasks)*100)
            else:
                average_of_task = 0
            
            return average_of_task

        list_of_projects = Task.objects.filter(assigned_to=request.user.id).distinct()
        distinct_projects = []
        for project in list_of_projects:
            if project.project.project_name not in distinct_projects:
                distinct_projects.append(project.project.project_name)
        percentage_of_project = []
        for project in distinct_projects:
            percentage = average_calculation(0,0,project,from_date_2_with_time_and_seconds,to_date_2_with_11_55_pm)
            percentage_of_project.append(percentage)

        # team members 
        department_name = request.user.department
        print(department_name)
        
        list_of_department_members = []
        department_members = CustomUser.objects.filter(department=department_name).distinct()
        for i in department_members:
            
            total_tasks = Task.objects.filter(assigned_to=i.id,task_created_at__gte=from_date_2_with_time_and_seconds,task_created_at__lte=to_date_2_with_11_55_pm).count()
            completed_tasks = Task.objects.filter(assigned_to=i.id,task_created_at__gte=from_date_2_with_time_and_seconds,task_created_at__lte=to_date_2_with_11_55_pm)
            
            team_count_of_completed = 0
            team_count_completedtask_by_duedate = 0
            team_count_completedtask_after_duedate = 0

            for task in completed_tasks:
                if task.task_completed_at is not None:
                    duedate = task.due_date
                    str_completedate = str(task.task_completed_at).split(' ')[0]
                    completedate = datetime.strptime(str_completedate,"%Y-%m-%d").date()
                    if duedate < completedate:
                        team_count_of_completed+=1
                        team_count_completedtask_after_duedate+=1
                    else:
                        team_count_of_completed+=1
                        team_count_completedtask_by_duedate+=1

            average_of_task =0
            team_cal_completedtask_by_duedate = 0
            team_cal_completedtask_after_duedate = 0

            if team_count_completedtask_after_duedate:
                team_cal_completedtask_after_duedate = int((team_count_completedtask_after_duedate/total_tasks)*100)
            if team_count_completedtask_by_duedate:
                team_cal_completedtask_by_duedate = int((team_count_completedtask_by_duedate/total_tasks)*100)
            if team_count_of_completed:
                average_of_task = int((team_count_of_completed/total_tasks)*100)
            

            
            print(i,'name')
            print('total_count_tasks',total_tasks)
            print( team_count_of_completed,' count_of_completed_tasks')
            print('average',average_of_task)
            
            print('------------')
            
            final_ = [i.username,average_of_task,i.profile_picture,team_cal_completedtask_by_duedate,team_cal_completedtask_after_duedate]
            list_of_department_members.append(final_)
      
        context ={
            'average_lead_by_duedate':cal_completedtask_by_duedate,
            'average_lead':average_of_task_lead,
            'average_lead_after_duedate':cal_completedtask_after_duedate,
            'from_date':from_date_,
            'to_date':to_date_,
            'command_for_task_':command_for_task_,
            "labels_of_chart":distinct_projects,
            "values_of_chart":percentage_of_project,
            "list_of_department_members":list_of_department_members
        }
        return render(request,'reportview_filter.html',context)
    
    return HttpResponse('<h2>sorry</h2>')

@login_required
def profile_update_view(request,pk):
    user = CustomUser.objects.get(id=pk)
    print('1')
    if request.method == "POST" and request.FILES.get('profile_picture'):
        profile_picture_ = request.FILES['profile_picture']
        print('2')
        if profile_picture_:
            user.profile_picture = profile_picture_
            user.save()
            print('3')
            return JsonResponse({"message": "Profile updated successfully!","file":'/media/{profile_picture_}'})
    print('4')
    return JsonResponse({"message": "Profile!"})


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
    start_of_lastmonth = end_of_lastmonth.replace(day=1)

    today_task = Task.objects.filter(assigned_to=request.user.id,due_date=today)
    yesterday = Task.objects.filter(assigned_to =request.user.id,due_date=yesterday)
    this_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_week,due_date__lte=end_of_week)
    last_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_lastweek,due_date__lte=end_of_lastweek)
    this_month = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_month,due_date__lte=end_of_month)
    last_month = Task.objects.filter(assigned_to=request.user.id,due_date__lte=end_of_lastmonth,due_date__gte=start_of_lastmonth)
    total_count = len(today_task)+len(yesterday)+len(this_week)+len(last_week)+len(this_month)+len(last_month)+len(last_month)
    users_project = Task.objects.filter(assigned_to=request.user.id).distinct()
    project_list = {}
    for task in users_project:
        if task.project.project_name not in project_list:
            task_count = len(Task.objects.filter(project=task.project,assigned_to=request.user.id))
            project_list[task.project.project_name] = task_count
    username = Task.objects.filter(assigned_to=request.user.id).first()
    department= request.user.department
    context ={
        'today_task':today_task,
        'yesterday':yesterday, 
        'this_week':this_week,
        'last_week':last_week,
        'this_month':this_month,
        'last_month':last_month,
        'department':department,
        'total_count':total_count,
        'department':department,
        'projects':project_list
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
    start_of_lastmonth = end_of_lastmonth.replace(day=1)

    department = Task.objects.filter(assigned_to=request.user.id).first()
    users_project = Task.objects.filter(assigned_to=request.user.id).distinct()
    project_list = {}
    for task in users_project:
        if task.project.project_name not in project_list:
            task_count = len(Task.objects.filter(project=task.project,assigned_to=request.user.id))
            project_list[task.project.project_name] = task_count
    
    if name =="Pending" or name =="In progress" or name =="Completed":
        project_name = ''
        today_task = Task.objects.filter(assigned_to=request.user.id,due_date=today,status = name)
        yesterday = Task.objects.filter(assigned_to =request.user.id,due_date=yesterday,status = name)
        this_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_week,due_date__lte=end_of_week,status = name)
        last_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_lastweek,due_date__lte=end_of_lastweek,status = name)
        this_month = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_month,due_date__lte=end_of_month,status = name)
        last_month = Task.objects.filter(assigned_to=request.user.id,due_date__lte=end_of_lastmonth,due_date__gte=start_of_lastmonth,status = name)
        total_count = len(today_task)+len(yesterday)+len(this_week)+len(last_week)+len(this_month)+len(last_month)+len(last_month)
    elif name == 'all':
        project_name = ""
        today_task = Task.objects.filter(assigned_to=request.user.id,due_date=today)
        yesterday = Task.objects.filter(assigned_to =request.user.id,due_date=yesterday)
        this_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_week,due_date__lte=end_of_week)
        last_week = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_lastweek,due_date__lte=end_of_lastweek)
        this_month = Task.objects.filter(assigned_to=request.user.id,due_date__gte=start_of_month,due_date__lte=end_of_month)
        last_month = Task.objects.filter(assigned_to=request.user.id,due_date__lte=end_of_lastmonth,due_date__gte=start_of_lastmonth)
        total_count = len(today_task)+len(yesterday)+len(this_week)+len(last_week)+len(this_month)+len(last_month)+len(last_month)
    else:
        project_id = Project.objects.filter(project_name=name).first()
        project_name = name
        today_task = Task.objects.filter(project=project_id.id,assigned_to=request.user.id,due_date=today)
        yesterday = Task.objects.filter(project=project_id.id,assigned_to =request.user.id,due_date=yesterday)
        this_week = Task.objects.filter(project=project_id.id,assigned_to=request.user.id,due_date__gte=start_of_week,due_date__lte=end_of_week)
        last_week = Task.objects.filter(project=project_id.id,assigned_to=request.user.id,due_date__gte=start_of_lastweek,due_date__lte=end_of_lastweek)
        this_month = Task.objects.filter(project=project_id.id,assigned_to=request.user.id,due_date__gte=start_of_month,due_date__lte=end_of_month)
        last_month = Task.objects.filter(project=project_id.id,assigned_to=request.user.id,due_date__lte=end_of_lastmonth,due_date__gte=start_of_lastmonth)
        total_count = len(today_task)+len(yesterday)+len(this_week)+len(last_week)+len(this_month)+len(last_month)+len(last_month)

    department= request.user.department
    context ={
        'today_task':today_task,
        'yesterday':yesterday,
        'this_week':this_week,
        'last_week':last_week,
        'this_month':this_month,
        'last_month':last_month,
        'department':department,
        'total_count':total_count,
        'project_name':project_name,
        'projects':project_list
    }
    return render(request,'dashboard.html',context)

@login_required
def update_task(request,pk):
    task = Task.objects.get(assigned_to=request.user.id,id=pk)
    if request.method == "POST":
        form = taskform(data=request.POST,files=request.FILES,instance=task)
        audio_f = request.FILES.get('audio')
        task_selection = request.POST.get('task_selection')
        files = request.FILES.getlist('document')
        print(task_selection)
        if form.is_valid():
            print('comes1')
            if files:
                for file in files:
                    doc_instance = multi_document(task_id=pk,document=file)
                    doc_instance.save()
                    print('document done ')
            if audio_f:
                task.audio = audio_f
            if task_selection:
                print(task_selection)
                task.task_depended_on = int(task_selection)
                struck_time = datetime.now()
                format_struct_time = struck_time.strftime("%Y-%m-%d %H:%M:%S")
                task.struck_time_start_at = struck_time
                task.save()
                print('done -1')
            form.save()
            return redirect('dashboard')
        else:
            print('Form is not valid:', form.errors)
    files_doc = multi_document.objects.filter(task_id=pk)
    files ={}
    if files_doc:
        for file in files_doc:
            filename = str(file).split('/')[-1]
            files[filename] = file
    form = taskform(instance=task)
    users = CustomUser.objects.filter(department=request.user.department).exclude(assigned_to=request.user.id)
    # task = Task.objects.all()
    print(users)
    url_to = 0
    return render(request,'update_tasks.html',{'tasks':task,'form':form,'url_to':url_to,'users':users,'files':files})
  
@login_required
def filter_search(request):
    users_project = Task.objects.filter(assigned_to=request.user.id).distinct()
    project_list = {}
    for task in users_project:
        if task.project.project_name not in project_list:
            task_count = len(Task.objects.filter(project=task.project,assigned_to=request.user.id))
            project_list[task.project.project_name] = task_count
    department= request.user.department
    if request.method =="POST":
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        project = request.POST.get('project')
        project_form = projectfilterform(request.POST)
        filter_task = Task.objects.filter(assigned_to=request.user.id,due_date__gte=from_date,due_date__lte=to_date,project=project).order_by('due_date')
        return render(request,"filter.html",context={'department':department,'filter_task':filter_task,'project_form':project_form,'from_date':from_date,'to_date':to_date,'projects':project_list})
    project_form = projectfilterform()

    return render(request,"filter.html",context={'department':department,'project_form':project_form,'projects':project_list})

@login_required
def over_due(request):
    users_project = Task.objects.filter(assigned_to=request.user.id).distinct()
    project_list = {}
    for task in users_project:
        if task.project.project_name not in project_list:
            task_count = len(Task.objects.filter(project=task.project,assigned_to=request.user.id))
            project_list[task.project.project_name] = task_count
    department= request.user.department
    today = timezone.now().date()
    over_due_tasks = Task.objects.filter(assigned_to=request.user.id,due_date__lt=today).filter(Q(status="In progress") | Q(status="Pending")).order_by('due_date')
    return render(request,'overdue_task.html',{"overdue_task":over_due_tasks,'department':department,'projects':project_list})



@login_required
def add_user(request):
    users_project = Task.objects.filter(assigned_to=request.user.id).distinct()
    project_list = {}
    for task in users_project:
        if task.project.project_name not in project_list:
            task_count = len(Task.objects.filter(project=task.project,assigned_to=request.user.id))
            project_list[task.project.project_name] = task_count
    department= request.user.department
    if request.method =='POST':
        form = CustomUserForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'User has been created successfully !')
            return redirect('add_user')
        else:
            messages.error(request,'error')
            return render(request,'add_user.html',{'form':form,'projects':project_list})
    form =CustomUserForm()
    return render(request,'add_user.html',{'form':form,'department':department,'projects':project_list})


@login_required
def Team_mem(request):
    users_project = Task.objects.filter(assigned_to=request.user.id).distinct()
    project_list = {}
    for task in users_project:
        if task.project.project_name not in project_list:
            task_count = len(Task.objects.filter(project=task.project,assigned_to=request.user.id))
            project_list[task.project.project_name] = task_count
    department= request.user.department
    members = CustomUser.objects.filter(department=request.user.department).exclude(username=request.user).order_by('username')
    mem_dict ={}
    for i in members:
        pending =0
        in_progress=0
        mem_dict[i.username]={'pending':pending,'in_progress':in_progress,'id':i.id}
        mem = Task.objects.filter(assigned_to=i)
        for k in mem:
            if k.status =="In progress":
                in_progress+=1
            else:
                pending+=1
        mem_dict[i.username]['pending']=pending
        mem_dict[i.username]["in_progress"]=in_progress
    
    other_department_mem = Task.objects.filter(created_by = request.user.id).distinct()
    print(other_department_mem,'dddd')
    list_of_memebers = []
    for spec_user in other_department_mem:
        user = CustomUser.objects.filter(username = spec_user.assigned_to).exclude(department=request.user.department).first()
        print(user,'s')
        if user:
            if user.username not in list_of_memebers:
                list_of_memebers.append(user.username)
    print(list_of_memebers)
    other_mem_list = {}
    for i in list_of_memebers:
        username_ = CustomUser.objects.filter(username=i).first()
        pending =0
        in_progress=0
        other_mem_list[username_.username]={'pending':pending,'in_progress':in_progress,'id':username_.id}
        mem = Task.objects.filter(assigned_to=username_.id)
        for k in mem:
            if k.status =="In progress":
                in_progress+=1
            else:
                pending+=1
        other_mem_list[username_.username]['pending']=pending
        other_mem_list[username_.username]["in_progress"]=in_progress
    print(other_mem_list)
    return render(request,'team_mem.html',{"mem_dict":mem_dict,'department':department,'other_mem_list':other_mem_list,'projects':project_list})

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
    start_of_lastmonth = end_of_lastmonth.replace(day=1)

    today_task = Task.objects.filter(assigned_to=pk,due_date=today)
    yesterday = Task.objects.filter(assigned_to =pk,due_date=yesterday)
    this_week = Task.objects.filter(assigned_to=pk,due_date__gte=start_of_week,due_date__lte=end_of_week)
    last_week = Task.objects.filter(assigned_to=pk,due_date__gte=start_of_lastweek,due_date__lte=end_of_lastweek)
    this_month = Task.objects.filter(assigned_to=pk,due_date__gte=start_of_month,due_date__lte=end_of_month)
    last_month = Task.objects.filter(assigned_to=pk,due_date__lte=end_of_lastmonth,due_date__gte=start_of_lastmonth)
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

@login_required
def new_task_creation(request):
    users_project = Task.objects.filter(assigned_to=request.user.id).distinct()
    project_list = {}
    for task in users_project:
        if task.project.project_name not in project_list:
            task_count = len(Task.objects.filter(project=task.project,assigned_to=request.user.id))
            project_list[task.project.project_name] = task_count
    department= request.user.department
    members = CustomUser.objects.filter(department=request.user.department).exclude(id=request.user.id).order_by("id")
    departments_names = CustomUser.objects.all()
    departments = []
    for department_name in departments_names:
        if department_name.department not in departments:
            departments.append(department_name.department)

    if request.method == 'POST':
        assign11 = request.POST.get('assigned_to')
        print(assign11)
        assign = CustomUser.objects.get(username=assign11)
        form = Taskcreation_form(data=request.POST)
        if form.is_valid():
            task_instance = form.save(commit=False)
            task_instance.assigned_to= assign
            task_instance.created_by = request.user
            task_instance.save()
            messages.success(request,"Your Task has been created successfully!")
            return redirect('new_task_creation')
        return render(request,'new_task.html',{"form":form,"members":members,'department':department,'projects':project_list})
    form = Taskcreation_form()
    print(departments)
    return render(request,'new_task.html',{"form":form,"members":members,'departments':departments,'department':department,'projects':project_list})

def project_creation(request):
    users_project = Task.objects.filter(assigned_to=request.user.id).distinct()
    project_list = {}
    for task in users_project:
        if task.project.project_name not in project_list:
            task_count = len(Task.objects.filter(project=task.project,assigned_to=request.user.id))
            project_list[task.project.project_name] = task_count
    department= request.user.department
    if request.method == "POST":
        form = project_form(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your project has been created successfully!")
            return redirect('project_creation')
        return render(request,"project_creation.html",{'form':form,"department":department,"projects":project_list})
    form = project_form()
    return render(request,'project_creation.html',{'form':form,"department":department,"projects":project_list})

def profile_view(request,pk=None):
    user = CustomUser.objects.get(id=pk)
    if request.method == "POST":
        userupdate = CustomUserForm(data=request.POST,instance=user)
        if userupdate.is_valid():
            userupdate.save()
            new_password = request.POST.get('password')
            if new_password:
                user.set_password(new_password)
            return redirect('Team_mem')
        else:
            return render(request,'update_profile.html',{'form':userupdate})
    userupdate = CustomUserForm(instance=user)
    return render(request,'update_profile.html',{'form':userupdate,'id':user.id})


def delete_user(request,pk):
    user = CustomUser.objects.get(id=pk)
    if user:
        user.delete()
        return redirect('Team_mem')
    return HttpResponse('<h1>Sorry</h1>')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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
        else:
            messages.error(request,"Invalid username or password")
            return render(request,'login.html',{'form':form})

    form= loginForm()
    return render(request,'login.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect('login')


def send_mail_(request):
    send_mail_view.delay()
    return HttpResponse('mail has been sent to your email')

def mailattime(request):
    schedule,created=CrontabSchedule.objects.get_or_create(hour=16,minute=59)
    task = PeriodicTask.objects.create(crontab=schedule,name="mail_task"+"1",task='task_pro.task.send_mail_view')
    return HttpResponse("success")


def getuser_department(request,name):
    print(name)
    if request.method == "GET":
        try:
            users_list = CustomUser.objects.filter(department=name)
            users_list_ = [{'username':i.username } for i in users_list]
            return JsonResponse({'users_list':users_list_})
        except CustomUser.DoesNotExist:
            return JsonResponse({'error':'Invalid request'},status=400)

def get_tasks_for_user(request,user_id):
    if request.method == 'GET':
        try:
            tasks = Task.objects.filter(assigned_to=user_id).exclude(status="Completed")
            task_data = [{'id':task.id,'title':task.title} for task in tasks]
            return JsonResponse({'user_tasks':task_data})
        except Task.DoesNotExist:
            return JsonResponse({'tasks':[]})
    
    return JsonResponse({'error':'Invalid request'},status =400)

def waiting_user_data(request,id):
    if request.method == 'GET':
        try:
            user = Task.objects.get(id=id)
            return JsonResponse({'user_data': {'name': user.due_date}})
        except CustomUser.DoesNotExist:
            return JsonResponse({'user_data':[]})
    return JsonResponse({'error'})


@login_required
def report_view(request):
    total_task_retrival = Task.objects.filter(assigned_to=request.user.id).count()
    completed_tasks = Task.objects.filter(assigned_to=request.user.id,incomplete=False)
    count_of_completed = 0
    count_completedtask_by_duedate = 0
    count_completedtask_after_duedate = 0
    for task in completed_tasks:
        if task.task_completed_at is not None:
            duedate = task.due_date
            str_completedate = str(task.task_completed_at).split(' ')[0]
            completedate = datetime.strptime(str_completedate,"%Y-%m-%d").date()
            if duedate < completedate:
                count_of_completed+=1
                count_completedtask_after_duedate+=1
            else:
                count_of_completed+=1
                count_completedtask_by_duedate+=1
            print(duedate,'duedate')
            print(completedate,'completed')
            print(duedate < completedate)
    average_of_task_lead =None
    # print(cal_completedtask_by_duedate,"cal_completedtask_by_duedate-------------")
    print(count_of_completed,'count_of_completed')
    over_cal_average_of_task_lead = 0
    cal_completedtask_by_duedate = 0
    cal_completedtask_after_duedate = 0

    if count_completedtask_after_duedate:
        cal_completedtask_after_duedate = int((count_completedtask_after_duedate/total_task_retrival)*100)
    if count_completedtask_by_duedate:
        cal_completedtask_by_duedate = int((count_completedtask_by_duedate/total_task_retrival)*100)
    if count_of_completed:
        average_of_task_lead = int((count_of_completed/total_task_retrival)*100)
    command_for_task_ = None
    color_of_bar = None
    if average_of_task_lead >= 90:
        command_for_task_ = '😀 Very Good!'
        color_of_bar ="#2fc30d"
        color_of_bar ="8ff090"
    elif average_of_task_lead >= 50:
        command_for_task_ ='🙂 ok'
        color_of_bar ="#dfe159"
    elif average_of_task_lead >=20:
        command_for_task_ ="🙁 Consider"
        color_of_bar ="#f3c349"
    else:
        command_for_task_ = "😢 bad"
        color_of_bar ="#ee720d"

    def average_calculation(start,end,project_name):
        today = timezone.now().date()
        total_tasks = None
        completed_tasks = None
        if start == 0 and end == 0:
            total_tasks = Task.objects.filter(assigned_to=request.user.id,project__project_name=project_name).count()
            completed_tasks = Task.objects.filter(assigned_to=request.user.id,project__project_name=project_name)
        elif end == 0 and project_name == 0:
            total_tasks = Task.objects.filter(due_date=start,assigned_to=request.user.id).count()
            completed_tasks = Task.objects.filter(assigned_to=request.user.id,due_date=start,incomplete=False)
        else:
            total_tasks = Task.objects.filter(assigned_to=request.user.id,due_date__lte=end,due_date__gte=start).count()
            completed_tasks = Task.objects.filter(assigned_to=request.user.id,due_date__lte=end,due_date__gte=start)

        count_of_completed = 0
        for task in completed_tasks:
            if task.task_completed_at is not None:
                count_of_completed+=1
        average_of_task =None
        if count_of_completed:
            average_of_task = int((count_of_completed/total_tasks)*100)
        else:
            average_of_task = 0
        
        return average_of_task
    
    today = timezone.now().date()
    yesterday = today -timedelta(days=1)
    yesterday_average = average_calculation(yesterday,0,0)
    today_average = average_calculation(today,0,0)

    for_last_week = today - timedelta(days=today.weekday())
    last_week_start = for_last_week - timedelta(days=7)
    last_week_end = for_last_week - timedelta(days=1)

    last_week_average = average_calculation(last_week_start,last_week_end,0)

    this_week_start = today - timedelta(days=today.weekday())
    this_week_end = for_last_week + timedelta(days=6)

    this_week_average = average_calculation(this_week_start,this_week_end,0)

    start_of_month = today.replace(day=1)
    end_of_lastmonth = start_of_month - timedelta(days=1)
    start_of_lastmonth = end_of_lastmonth.replace(day=1)

    lastmonth_average = average_calculation(start_of_lastmonth,end_of_lastmonth,0)

    start_of_this_month = today.replace(day=1)
    next_month = start_of_this_month + timedelta(days=32)
    start_of_nextmonth = next_month.replace(day=1)
    end_of_this_month = start_of_nextmonth - timedelta(days=1)

    this_month_average = average_calculation(start_of_this_month,end_of_this_month,0)


    start_of_the_year = today.replace(day=1,month=1)
    last_year_end = start_of_the_year - timedelta(days=1)
    last_year_start = last_year_end.replace(day=1,month=1)

    last_year_average = average_calculation(last_year_start,last_year_end,0)

    start_of_this_year = today.replace(day=1,month=1)
    end_of_this_year = start_of_this_year.replace(day=31,month=12)
    currentyear_average = average_calculation(start_of_this_year,end_of_this_year,0)

    list_of_projects = Task.objects.filter(assigned_to=request.user.id).distinct()
    distinct_projects = []
    for project in list_of_projects:
        if project.project.project_name not in distinct_projects:
            distinct_projects.append(project.project.project_name)
    
    percentage_of_project = []
    for project in distinct_projects:
        percentage = average_calculation(0,0,project)
        percentage_of_project.append(percentage)


    # team members 
    department_name = request.user.department
    print(department_name)
    
    list_of_department_members = []
    department_members = CustomUser.objects.filter(department=department_name).distinct()
    for i in department_members:
        
        total_tasks = Task.objects.filter(assigned_to=i.id).count()
        completed_tasks = Task.objects.filter(assigned_to=i.id)
        
        team_count_of_completed = 0
        team_count_completedtask_by_duedate = 0
        team_count_completedtask_after_duedate = 0

        

        for task in completed_tasks:
            if task.task_completed_at is not None:
                duedate = task.due_date
                str_completedate = str(task.task_completed_at).split(' ')[0]
                completedate = datetime.strptime(str_completedate,"%Y-%m-%d").date()
                if duedate < completedate:
                    team_count_of_completed+=1
                    team_count_completedtask_after_duedate+=1
                else:
                    team_count_of_completed+=1
                    team_count_completedtask_by_duedate+=1

        average_of_task =0
        team_cal_completedtask_by_duedate = 0
        team_cal_completedtask_after_duedate = 0

        if team_count_completedtask_after_duedate:
            team_cal_completedtask_after_duedate = int((team_count_completedtask_after_duedate/total_tasks)*100)
        if team_count_completedtask_by_duedate:
            team_cal_completedtask_by_duedate = int((team_count_completedtask_by_duedate/total_tasks)*100)
        if team_count_of_completed:
            average_of_task = int((team_count_of_completed/total_tasks)*100)
        

        
        print(i,'name')
        print('total_count_tasks',total_tasks)
        print( team_count_of_completed,' count_of_completed_tasks')
        print('average',average_of_task)
        
        print('------------')
        
        final_ = [i.username,average_of_task,i.profile_picture,team_cal_completedtask_by_duedate,team_cal_completedtask_after_duedate]
        list_of_department_members.append(final_)

    print(list_of_department_members)
    profile_pic = request.user.profile_picture
    print(profile_pic,'ffffffffffffff')
    print(team_cal_completedtask_by_duedate)
    print(team_count_completedtask_after_duedate,'ssss')


    context={
        'profile':profile_pic,
        'average_lead_by_duedate':cal_completedtask_by_duedate,
        'average_lead_after_duedate':cal_completedtask_after_duedate,
        'average_lead':average_of_task_lead,
        "command_for_task_":command_for_task_,
        "color_of_bar":color_of_bar,
        "average_today":today_average,
        "average_yesterday":yesterday_average,
        "average_thisweek":this_week_average,
        "average_lastweek":last_week_average,
        "average_thismonth":this_month_average,
        "average_lastmonth":lastmonth_average,
        "average_thisyear":currentyear_average,
        "average_lastyear":last_year_average,
        "labels_of_chart":distinct_projects,
        "values_of_chart":percentage_of_project,
        "list_of_department_members":list_of_department_members
        }

    return render(request,'reportview.html',context)
