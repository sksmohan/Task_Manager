# Generated by Django 4.2.16 on 2024-11-29 08:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task_pro', '0008_rename_depended_on_task_task_depended_on'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='struck_time',
            new_name='struck_time_start_at',
        ),
    ]
