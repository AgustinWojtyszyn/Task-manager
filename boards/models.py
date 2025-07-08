from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Board(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards', verbose_name="Propietario")
    members = models.ManyToManyField(User, related_name='boards', blank=True, verbose_name="Miembros")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Tablero"
        verbose_name_plural = "Tableros"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('board_detail', kwargs={'pk': self.pk})


class TaskList(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='lists', verbose_name="Tablero")
    position = models.PositiveIntegerField(default=0, verbose_name="Posición")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        ordering = ['position']
        verbose_name = "Lista de tareas"
        verbose_name_plural = "Listas de tareas"

    def __str__(self):
        return f"{self.name} ({self.board.name})"

    def get_next_position(self):
        """Get the next position for a new task in this list"""
        last_task = self.tasks.order_by('-position').first()
        return (last_task.position + 1) if last_task else 0


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('L', 'Baja'),
        ('M', 'Media'),
        ('H', 'Alta'),
        ('C', 'Crítica'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    due_date = models.DateField(null=True, blank=True, verbose_name="Fecha límite")
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M', verbose_name="Prioridad")
    labels = models.CharField(max_length=200, blank=True, verbose_name="Etiquetas", 
                             help_text="Separar etiquetas con comas")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_tasks', verbose_name="Asignado a")
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks', verbose_name="Lista")
    position = models.PositiveIntegerField(default=0, verbose_name="Posición")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    completed = models.BooleanField(default=False, verbose_name="Completada")

    class Meta:
        ordering = ['position']
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Check if the task is overdue"""
        return self.due_date and self.due_date < timezone.now().date() and not self.completed

    @property
    def priority_color(self):
        """Return CSS class for priority color"""
        colors = {
            'L': 'success',
            'M': 'warning',
            'H': 'danger',
            'C': 'dark'
        }
        return colors.get(self.priority, 'secondary')

    @property
    def labels_list(self):
        """Return labels as a list"""
        if self.labels:
            return [label.strip() for label in self.labels.split(',') if label.strip()]
        return []

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name="Tarea")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    content = models.TextField(verbose_name="Contenido")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"

    def __str__(self):
        return f"Comentario de {self.author.username} en {self.task.title}"
