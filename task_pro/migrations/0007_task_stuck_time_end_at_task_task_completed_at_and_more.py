# Generated by Django 4.2.16 on 2024-11-29 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_pro', '0006_rename_created_at_task_task_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='stuck_time_end_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='task_completed_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='waiting_for',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='waiting_time_start_at',
            field=models.DateField(null=True),
        ),
    ]