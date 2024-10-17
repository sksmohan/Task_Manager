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
    path("send_mail_",send_mail_,name='send_mail_')

]