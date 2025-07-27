from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
import json
import csv
from .models import Board, TaskList, Task, TaskComment
from .forms import (
    CustomUserCreationForm, BoardForm, TaskListForm, 
    TaskForm, QuickTaskForm, TaskCommentForm, TaskMoveForm
)


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Trello Clone.')
            return redirect('board_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def board_list(request):
    """List all boards for the current user"""
    owned_boards = Board.objects.filter(owner=request.user)
    member_boards = Board.objects.filter(members=request.user)
    
    context = {
        'owned_boards': owned_boards,
        'member_boards': member_boards,
    }
    return render(request, 'boards/board_list.html', context)


@login_required
def board_detail(request, pk):
    """Display board with all its lists and tasks"""
    board = get_object_or_404(Board, pk=pk)
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        messages.error(request, 'No tienes permiso para ver este tablero.')
        return redirect('board_list')
    
    lists = board.lists.prefetch_related('tasks__assigned_to').all()
    
    context = {
        'board': board,
        'lists': lists,
        'quick_task_form': QuickTaskForm(),
        'task_list_form': TaskListForm(),
    }
    return render(request, 'boards/board_detail.html', context)


@login_required
def board_create(request):
    """Create a new board"""
    if request.method == 'POST':
        form = BoardForm(request.POST, user=request.user)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f'Tablero "{board.name}" creado exitosamente.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = BoardForm(user=request.user)
    
    return render(request, 'boards/board_form.html', {'form': form, 'title': 'Crear Tablero'})


@login_required
def board_edit(request, pk):
    """Edit an existing board"""
    board = get_object_or_404(Board, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tablero "{board.name}" actualizado exitosamente.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = BoardForm(instance=board, user=request.user)
    
    return render(request, 'boards/board_form.html', {
        'form': form, 
        'title': 'Editar Tablero',
        'board': board
    })


@login_required
def board_delete(request, pk):
    """Delete a board"""
    board = get_object_or_404(Board, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        board_name = board.name
        board.delete()
        messages.success(request, f'Tablero "{board_name}" eliminado exitosamente.')
        return redirect('board_list')
    
    return render(request, 'boards/board_confirm_delete.html', {'board': board})


@login_required
def task_list_create(request, board_pk):
    """Create a new task list"""
    board = get_object_or_404(Board, pk=board_pk)
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        messages.error(request, 'No tienes permiso para modificar este tablero.')
        return redirect('board_list')
    
    if request.method == 'POST':
        form = TaskListForm(request.POST)
        if form.is_valid():
            task_list = form.save(commit=False)
            task_list.board = board
            task_list.save()
            messages.success(request, f'Lista "{task_list.name}" creada exitosamente.')
            return redirect('board_detail', pk=board.pk)
    
    return redirect('board_detail', pk=board.pk)


@login_required
def task_list_edit(request, pk):
    lista = get_object_or_404(TaskList, pk=pk)
    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre')
        if nuevo_nombre:
            lista.name = nuevo_nombre
            lista.save()
            messages.success(request, 'Nombre de la lista actualizado.')
            return redirect('board_detail', pk=lista.board.pk)
    return render(request, 'boards/task_list_edit.html', {'lista': lista})


@login_required
def task_list_delete(request, pk):
    """Delete a task list"""
    task_list = get_object_or_404(TaskList, pk=pk)
    board = task_list.board
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        messages.error(request, 'No tienes permiso para modificar este tablero.')
        return redirect('board_list')
    
    if request.method == 'POST':
        list_name = task_list.name
        task_list.delete()
        messages.success(request, f'Lista "{list_name}" eliminada exitosamente.')
        return redirect('board_detail', pk=board.pk)
    
    return render(request, 'boards/task_list_confirm_delete.html', {
        'task_list': task_list,
        'board': board
    })


@login_required
def task_create(request, board_pk, list_pk=None):
    """Create a new task"""
    board = get_object_or_404(Board, pk=board_pk)
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        messages.error(request, 'No tienes permiso para modificar este tablero.')
        return redirect('board_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, board=board, user=request.user)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Tarea "{task.title}" creada exitosamente.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskForm(board=board, user=request.user)
        if list_pk:
            task_list = get_object_or_404(TaskList, pk=list_pk, board=board)
            form.fields['task_list'].initial = task_list
    
    return render(request, 'boards/task_form.html', {
        'form': form,
        'board': board,
        'title': 'Crear Tarea'
    })


@login_required
def quick_task_create(request, list_pk):
    """Create a quick task via AJAX"""
    task_list = get_object_or_404(TaskList, pk=list_pk)
    board = task_list.board
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    if request.method == 'POST':
        form = QuickTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.task_list = task_list
            task.save()
            return JsonResponse({
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'priority': task.get_priority_display(),
                    'priority_color': task.priority_color,
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def task_detail(request, pk):
    """Display task details"""
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        messages.error(request, 'No tienes permiso para ver esta tarea.')
        return redirect('board_list')
    
    comments = task.comments.select_related('author').all()
    
    if request.method == 'POST':
        comment_form = TaskCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comentario añadido exitosamente.')
            return redirect('task_detail', pk=task.pk)
    else:
        comment_form = TaskCommentForm()
    
    context = {
        'task': task,
        'board': board,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'boards/task_detail.html', context)


@login_required
def task_edit(request, pk):
    """Edit a task"""
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        messages.error(request, 'No tienes permiso para modificar esta tarea.')
        return redirect('board_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, board=board, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tarea "{task.title}" actualizada exitosamente.')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, board=board, user=request.user)
    
    return render(request, 'boards/task_form.html', {
        'form': form,
        'task': task,
        'board': board,
        'title': 'Editar Tarea'
    })


@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        messages.error(request, 'No tienes permiso para modificar esta tarea.')
        return redirect('board_list')
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Tarea "{task_title}" eliminada exitosamente.')
        return redirect('board_detail', pk=board.pk)
    
    return render(request, 'boards/task_confirm_delete.html', {
        'task': task,
        'board': board
    })


@login_required
@require_POST
def task_move(request, pk):
    """Move a task to a different list via AJAX"""
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    try:
        data = json.loads(request.body)
        new_list_id = data.get('new_list_id')
        new_position = data.get('new_position', 0)
        
        # Validate new list belongs to the same board
        new_list = get_object_or_404(TaskList, pk=new_list_id, board=board)
        
        with transaction.atomic():
            old_list = task.task_list
            old_position = task.position
            
            # If moving within the same list, adjust positions
            if old_list == new_list:
                if new_position < old_position:
                    # Moving up in the same list
                    tasks_to_update = Task.objects.filter(
                        task_list=old_list,
                        position__gte=new_position,
                        position__lt=old_position
                    )
                    for t in tasks_to_update:
                        t.position += 1
                        t.save()
                elif new_position > old_position:
                    # Moving down in the same list
                    tasks_to_update = Task.objects.filter(
                        task_list=old_list,
                        position__gt=old_position,
                        position__lte=new_position
                    )
                    for t in tasks_to_update:
                        t.position -= 1
                        t.save()
            else:
                # Moving to a different list
                # Adjust positions in old list
                tasks_in_old_list = Task.objects.filter(
                    task_list=old_list,
                    position__gt=old_position
                )
                for t in tasks_in_old_list:
                    t.position -= 1
                    t.save()
                
                # Adjust positions in new list
                tasks_in_new_list = Task.objects.filter(
                    task_list=new_list,
                    position__gte=new_position
                )
                for t in tasks_in_new_list:
                    t.position += 1
                    t.save()
            
            # Update the task itself
            task.task_list = new_list
            task.position = new_position
            task.save()
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'new_list_id': new_list.id,
            'new_position': new_position
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def task_toggle_complete(request, pk):
    """Toggle task completion status"""
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    task.completed = not task.completed
    task.save()
    
    return JsonResponse({
        'success': True,
        'completed': task.completed
    })


@login_required
def export_board_csv(request, pk):
    """Export board tasks to CSV"""
    board = get_object_or_404(Board, pk=pk)
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        messages.error(request, 'No tienes permiso para exportar este tablero.')
        return redirect('board_list')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{board.name}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Lista', 'Tarea', 'Descripción', 'Fecha límite', 
        'Prioridad', 'Asignado a', 'Etiquetas', 'Completada'
    ])
    
    for task_list in board.lists.all():
        for task in task_list.tasks.all():
            writer.writerow([
                task_list.name,
                task.title,
                task.description,
                task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
                task.get_priority_display(),
                task.assigned_to.get_full_name() if task.assigned_to else '',
                task.labels,
                'Sí' if task.completed else 'No'
            ])
    
    return response


@login_required
def export_board_json(request, pk):
    """Export board tasks to JSON"""
    board = get_object_or_404(Board, pk=pk)
    
    # Check if user has access to this board
    if not (board.owner == request.user or request.user in board.members.all()):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    data = {
        'board': {
            'name': board.name,
            'description': board.description,
            'created_at': board.created_at.isoformat(),
        },
        'lists': []
    }
    
    for task_list in board.lists.all():
        list_data = {
            'name': task_list.name,
            'position': task_list.position,
            'tasks': []
        }
        
        for task in task_list.tasks.all():
            list_data['tasks'].append({
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'priority': task.get_priority_display(),
                'labels': task.labels_list,
                'assigned_to': task.assigned_to.get_full_name() if task.assigned_to else None,
                'completed': task.completed,
                'created_at': task.created_at.isoformat(),
            })
        
        data['lists'].append(list_data)
    
    response = JsonResponse(data, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="{board.name}.json"'
    return response


@login_required
def search_tasks(request):
    """Search tasks across all user's boards"""
    query = request.GET.get('q', '')
    
    if query:
        # Get all boards user has access to
        user_boards = Board.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        ).distinct()
        
        # Search tasks in those boards
        tasks = Task.objects.filter(
            task_list__board__in=user_boards
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(labels__icontains=query)
        ).select_related('task_list__board', 'assigned_to')
        
        paginator = Paginator(tasks, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    
    context = {
        'query': query,
        'page_obj': page_obj,
    }
    return render(request, 'boards/search_results.html', context)


from django.shortcuts import get_object_or_404, redirect
from .models import TaskList

@login_required
def editar_lista(request, lista_id):
    lista = get_object_or_404(TaskList, id=lista_id)
    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre')
        if nuevo_nombre:
            lista.name = nuevo_nombre
            lista.save()
            messages.success(request, 'Nombre de la lista actualizado.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
