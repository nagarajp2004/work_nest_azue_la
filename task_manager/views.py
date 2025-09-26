from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
import json

from .models import Task, User
from .forms import UserRegistrationForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'task_manager/register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'task_manager/dashboard.html')

@login_required
def get_tasks(request):
    """
    API endpoint to get tasks for the logged-in user.
    """
    my_tasks = Task.objects.filter(assigned_to=request.user).values(
        'id', 'title', 'description', 'status', 'assigned_by__username'
    )
    assigned_tasks = Task.objects.filter(assigned_by=request.user).values(
        'id', 'title', 'description', 'status', 'assigned_to__username'
    )
    
    return JsonResponse({
        'my_tasks': list(my_tasks),
        'assigned_tasks': list(assigned_tasks)
    })

@login_required
def get_assignable_users(request):
    """
    API endpoint to get users to whom the current user can assign tasks.
    A user can assign tasks to users with an equal or lower designation level.
    (Higher designation_level number means lower designation).
    """
    current_user_level = request.user.profile.designation_level
    assignable_users = User.objects.filter(
        profile__designation_level__gte=current_user_level
    ).exclude(id=request.user.id).values('id', 'username')
    
    return JsonResponse({'users': list(assignable_users)})


@login_required
@require_POST
def create_task(request):
    """
    API endpoint to create a new task.
    """
    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        assigned_to_id = data.get('assigned_to')

        if not title or not assigned_to_id:
            return JsonResponse({'error': 'Title and assigned user are required.'}, status=400)

        assigned_to_user = User.objects.get(id=assigned_to_id)
        current_user_level = request.user.profile.designation_level
        assigned_user_level = assigned_to_user.profile.designation_level

        # Security check: Ensure current user has the authority to assign the task
        if current_user_level > assigned_user_level:
            return JsonResponse({'error': 'You cannot assign tasks to users with a higher designation.'}, status=403)

        task = Task.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_to_user,
            assigned_by=request.user
        )
        return JsonResponse({'message': 'Task created successfully!', 'task_id': task.id})

    except User.DoesNotExist:
        return JsonResponse({'error': 'Assigned user not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def update_task_status(request, task_id):
    """
    API endpoint to update a task's status.
    """
    try:
        task = Task.objects.get(id=task_id)

        # Security check: Only the user the task is assigned to can update it
        if task.assigned_to != request.user:
            return HttpResponseForbidden("You are not authorized to update this task.")

        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status not in ['To Do', 'In Progress', 'Done']:
            return JsonResponse({'error': 'Invalid status value.'}, status=400)
            
        task.status = new_status
        task.save()
        
        return JsonResponse({'message': 'Status updated successfully!'})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
