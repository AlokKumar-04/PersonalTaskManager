from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import date, datetime
from django.urls import reverse
from django.http import HttpResponse
import csv
import io

from .models import Task
from .forms import TaskForm

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas



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



# CSV Export Views
@login_required
def export_tasks_csv(request):
    """Export user's tasks to CSV format"""
    # Get user's tasks
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="tasks_{request.user.username}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Title',
        'Description',
        'Priority',
        'Due Date',
        'Status',
        'Created Date',
        'Completed'
    ])
    
    # Write task data
    for task in tasks:
        writer.writerow([
            task.title,
            task.description or '',
            task.priority,
            task.due_date.strftime('%Y-%m-%d'),
            'Completed' if task.is_completed else 'Pending',
            task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Yes' if task.is_completed else 'No'
        ])
    
    return response

@login_required
def export_single_task_csv(request, task_id):
    """Export a single task to CSV format"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="task_{task.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Title',
        'Description',
        'Priority',
        'Due Date',
        'Status',
        'Created Date',
        'Completed'
    ])
    
    # Write task data
    writer.writerow([
        task.title,
        task.description or '',
        task.priority,
        task.due_date.strftime('%Y-%m-%d'),
        'Completed' if task.is_completed else 'Pending',
        task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'Yes' if task.is_completed else 'No'
    ])
    
    return response

# PDF Export Views
@login_required
def export_tasks_pdf(request):
    """Export user's tasks to PDF format"""
    # Get user's tasks
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="tasks_{request.user.username}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add title
    title = Paragraph(f"Task Report - {request.user.username}", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Add generation date
    date_para = Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style)
    story.append(date_para)
    story.append(Spacer(1, 12))
    
    # Add summary
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = tasks.filter(due_date__lt=timezone.now().date(), is_completed=False).count()
    
    summary_data = [
        ['Summary', ''],
        ['Total Tasks', str(total_tasks)],
        ['Completed', str(completed_tasks)],
        ['Pending', str(pending_tasks)],
        ['Overdue', str(overdue_tasks)]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Add tasks table
    if tasks.exists():
        heading = Paragraph("Task Details", heading_style)
        story.append(heading)
        story.append(Spacer(1, 12))
        
        # Prepare table data
        table_data = [['Title', 'Priority', 'Due Date', 'Status', 'Created']]
        
        for task in tasks:
            table_data.append([
                task.title[:30] + '...' if len(task.title) > 30 else task.title,
                task.priority,
                task.due_date.strftime('%Y-%m-%d'),
                'Completed' if task.is_completed else 'Pending',
                task.created_at.strftime('%Y-%m-%d')
            ])
        
        # Create table
        task_table = Table(table_data, colWidths=[2.5*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
        task_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(task_table)
    else:
        no_tasks = Paragraph("No tasks found.", normal_style)
        story.append(no_tasks)
    
    # Build PDF
    doc.build(story)
    return response

@login_required
def export_single_task_pdf(request, task_id):
    """Export a single task to PDF format"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="task_{task.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Custom style for task details
    detail_style = ParagraphStyle(
        'DetailStyle',
        parent=normal_style,
        fontSize=10,
        spaceAfter=6,
        leftIndent=20
    )
    
    # Add title
    title = Paragraph(f"Task Details: {task.title}", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Add generation date
    date_para = Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style)
    story.append(date_para)
    story.append(Spacer(1, 20))
    
    # Task details
    details = [
        ('Title:', task.title),
        ('Description:', task.description or 'No description provided'),
        ('Priority:', task.priority),
        ('Due Date:', task.due_date.strftime('%B %d, %Y')),
        ('Status:', 'Completed' if task.is_completed else 'Pending'),
        ('Created:', task.created_at.strftime('%B %d, %Y at %I:%M %p')),
        ('Owner:', task.user.username)
    ]
    
    for label, value in details:
        heading = Paragraph(label, heading_style)
        story.append(heading)
        detail = Paragraph(str(value), detail_style)
        story.append(detail)
        story.append(Spacer(1, 8))
    
    # Build PDF
    doc.build(story)
    return response

# Export options view
@login_required
def export_options(request):
    """Display export options page"""
    tasks = Task.objects.filter(user=request.user)
    context = {
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(is_completed=True).count(),
        'pending_tasks': tasks.filter(is_completed=False).count(),
        'overdue_tasks': tasks.filter(due_date__lt=timezone.now().date(), is_completed=False).count()
    }
    return render(request, 'tasks/export_options.html', context)