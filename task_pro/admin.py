from django.contrib import admin
from .models import Employee,Task, Project

# Register your models here.

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user','department']


class TaskAdmin(admin.ModelAdmin):
    list_display = ['title','assigned_to','created_by','status']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_name']

admin.site.register(Employee,EmployeeAdmin)
admin.site.register(Task,TaskAdmin)
admin.site.register(Project,ProjectAdmin)


admin.site.site_header = "Admin"
admin.site.site_title = "Admin"
admin.site.index_title = "Admin"
