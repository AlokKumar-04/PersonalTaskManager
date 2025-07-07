from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import date
from .models import Task
from .forms import TaskForm
from django.urls import reverse


# Create your views here.

def home(request):
    return render(request, 'doorway/home.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another one.')

        elif form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'doorway/registration.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('doorway:home')  
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')  


@login_required
def task_dashboard(request):
    
    tasks = Task.objects.filter(user=request.user)
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Handle completion status filter
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'completed':
        tasks = tasks.filter(is_completed=True)
    elif status_filter == 'pending':
        tasks = tasks.filter(is_completed=False)
    elif status_filter == 'overdue':
        tasks = tasks.filter(is_completed=False, due_date__lt=date.today())
    
    # Handle priority filter
    priority_filter = request.GET.get('priority', 'all')
    if priority_filter != 'all':
        tasks = tasks.filter(priority=priority_filter)
    
    # Handle sorting
    sort_by = request.GET.get('sort', 'due_date')
    if sort_by == 'title':
        tasks = tasks.order_by('title')
    elif sort_by == 'priority':
        # Custom ordering for priority: High, Medium, Low
        tasks = tasks.extra(
            select={'priority_order': "CASE WHEN priority='High' THEN 1 WHEN priority='Medium' THEN 2 ELSE 3 END"}
        ).order_by('priority_order')
    elif sort_by == 'created':
        tasks = tasks.order_by('-created_at')
    else:  # default to due_date
        tasks = tasks.order_by('due_date')
    
    # Get task statistics
    total_tasks = Task.objects.filter(user=request.user).count()
    pending_tasks = Task.objects.filter(user=request.user, is_completed=False).count()
    completed_tasks = Task.objects.filter(user=request.user, is_completed=True).count()
    overdue_tasks = Task.objects.filter(
        user=request.user, 
        is_completed=False, 
        due_date__lt=date.today()
    ).count()
    
    context = {
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'priority_choices': Task.PRIORITY_CHOICES,
        'today': date.today(),
    }
    
    return render(request, 'doorway/dashboard.html', context)


@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('doorway:dashboard')
    else:
        form = TaskForm()
    
    return render(request, 'doorway/create_task.html', {'form': form})


@login_required
def update_task(request, task_id):
    """Update an existing task"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_dashboard')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'doorway/update_task.html', {'form': form, 'task': task})

@login_required
def delete_task(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('doorway:dashboard')
    
    return render(request, 'doorway/delete_task.html', {'task': task})


"""Toggle task completion status"""
@login_required
def toggle_task_completion(request, task_id):
    
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.is_completed = not task.is_completed
    task.save()
    
    status = "completed" if task.is_completed else "reopened"
    messages.success(request, f'Task {status} successfully!')
    return redirect('doorway:dashboard')


"""View task details"""
@login_required
def task_detail(request, task_id):
    
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # Check if task is overdue
    is_overdue = not task.is_completed and task.due_date < date.today()
    
    context = {
        'task': task,
        'is_overdue': is_overdue,
        'today': date.today(),
    }
    
    return render(request, 'doorway/task_detail.html', context)

