# Generated by Django 5.2.3 on 2025-07-03 10:36

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='A short title for the task.', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Optional description of the task.')),
                ('due_date', models.DateField(default=datetime.date.today, help_text='Select the due date for the task.')),
                ('priority', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Medium', help_text='Set the task priority: Low, Medium, or High.', max_length=10)),
                ('is_completed', models.BooleanField(default=False, help_text='Mark as completed if the task is done.')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the task was created.')),
                ('user', models.ForeignKey(help_text='The user this task belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
