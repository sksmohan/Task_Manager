# Generated by Django 4.2.16 on 2024-12-02 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_pro', '0013_alter_task_waiting_time_start_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='waiting_for_username',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
