from django.contrib import admin
from .models import Task, Project
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('department', 'head'),
        }),
    )
    list_display=['username','department','head']

admin.site.register(CustomUser, CustomUserAdmin)
# Register your models here.


class TaskAdmin(admin.ModelAdmin):
    list_display = ['title','assigned_to','created_by','status']

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_name']

admin.site.register(Task,TaskAdmin)
admin.site.register(Project,ProjectAdmin)

admin.site.site_header = "Admin"
admin.site.site_title = "Admin"
admin.site.index_title = "Admin"