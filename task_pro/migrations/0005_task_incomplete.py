# Generated by Django 4.2.16 on 2024-11-29 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_pro', '0004_remove_task_dependent_task_task_depended_on_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='incomplete',
            field=models.BooleanField(default=False),
        ),
    ]