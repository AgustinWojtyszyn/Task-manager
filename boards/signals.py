from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import Task, Board, TaskList


@receiver(post_save, sender=Task)
def send_task_notification(sender, instance, created, **kwargs):
    """Send email notification when a task is created or assigned"""
    if instance.assigned_to and instance.assigned_to.email:
        if created:
            subject = f'Nueva tarea asignada: {instance.title}'
            message = f'''
Hola {instance.assigned_to.first_name or instance.assigned_to.username},

Se te ha asignado una nueva tarea:

Título: {instance.title}
Tablero: {instance.task_list.board.name}
Lista: {instance.task_list.name}
Prioridad: {instance.get_priority_display()}
Fecha límite: {instance.due_date or 'Sin fecha límite'}

Descripción:
{instance.description or 'Sin descripción'}

Puedes ver la tarea en el tablero para más detalles.

Saludos,
Equipo Trello Clone
            '''
        else:
            # Check if assignment changed
            try:
                old_instance = Task.objects.get(pk=instance.pk)
                if old_instance.assigned_to != instance.assigned_to:
                    subject = f'Tarea reasignada: {instance.title}'
                    message = f'''
Hola {instance.assigned_to.first_name or instance.assigned_to.username},

Se te ha reasignado una tarea:

Título: {instance.title}
Tablero: {instance.task_list.board.name}
Lista: {instance.task_list.name}
Prioridad: {instance.get_priority_display()}
Fecha límite: {instance.due_date or 'Sin fecha límite'}

Descripción:
{instance.description or 'Sin descripción'}

Puedes ver la tarea en el tablero para más detalles.

Saludos,
Equipo Trello Clone
                    '''
                else:
                    return  # No assignment change, don't send email
            except Task.DoesNotExist:
                return

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.assigned_to.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending email: {e}")


@receiver(post_save, sender=Board)
def create_default_lists(sender, instance, created, **kwargs):
    """Create default task lists when a new board is created"""
    if created:
        default_lists = [
            'Por hacer',
            'En progreso',
            'Terminado'
        ]
        
        for i, list_name in enumerate(default_lists):
            TaskList.objects.create(
                name=list_name,
                board=instance,
                position=i
            )


@receiver(pre_save, sender=Task)
def set_task_position(sender, instance, **kwargs):
    """Set task position if not provided"""
    if not instance.position and instance.task_list:
        instance.position = instance.task_list.get_next_position()


@receiver(pre_save, sender=TaskList)
def set_list_position(sender, instance, **kwargs):
    """Set list position if not provided"""
    if not instance.position and instance.board:
        last_list = TaskList.objects.filter(board=instance.board).order_by('-position').first()
        instance.position = (last_list.position + 1) if last_list else 0
