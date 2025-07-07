from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', help_text="The user this task belongs to.")
    title = models.CharField(max_length=200, help_text="A short title for the task.")
    description = models.TextField(blank=True, help_text="Optional description of the task.")
    due_date = models.DateField(default=date.today, help_text="Select the due date for the task.")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium',help_text="Set the task priority: Low, Medium, or High.")
    is_completed = models.BooleanField(default=False, help_text="Mark as completed if the task is done.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the task was created.")

    def __str__(self):
        return self.title

