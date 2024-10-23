from django.urls import path
from .views import *

urlpatterns =[
    path('dashboard', dashboard, name = "dashboard"),
    path('',login_view,name = "login"),
    path('admin_login',admin_login,name='admin_login'),
    path('logout/',logout_view,name='logout'),
    path('specific_task/<str:name>/',specific_task,name='specific_task'),
    path('update_task/<int:pk>/',update_task,name='update_task'),
    path('filter_search/',filter_search,name='filter_search'),
    path('over_due/',over_due,name='over_due'),
    path('test',test,name='test'),
    path('schedule_task',schedule_task,name="schedule_task"),
    path("send_mail_",send_mail_,name='send_mail_'),
    path('mailattime',mailattime,name="mailattime"),
    path('add_user',add_user,name="add_user"),
    path('Team_mem',Team_mem,name='Team_mem'),
    path('profile_update/<int:pk>/',profile_update,name='profile_update'),
    path('profile_task/<int:pk>/',profile_task_update,name="profile_task"),
    path('delete_task/<int:pk>',delete_task,name="delete_task"),
    path('new_task_creation',new_task_creation,name="new_task_creation"),
    path('project_creation',project_creation,name='project_creation')
]