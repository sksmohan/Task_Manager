# Generated by Django 4.2.16 on 2024-10-23 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_pro', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='Is_daily',
            field=models.BooleanField(default=False),
        ),
    ]
