from django.contrib import admin
from .models import Board, TaskList, Task, TaskComment


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__username')
    filter_horizontal = ('members',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'owner')
        }),
        ('Miembros', {
            'fields': ('members',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ('name', 'board', 'position', 'created_at')
    list_filter = ('board', 'created_at')
    search_fields = ('name', 'board__name')
    ordering = ('board', 'position')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_list', 'assigned_to', 'priority', 'due_date', 'completed', 'created_at')
    list_filter = ('priority', 'completed', 'due_date', 'created_at', 'task_list__board')
    search_fields = ('title', 'description', 'labels')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'task_list')
        }),
        ('Asignación y Prioridad', {
            'fields': ('assigned_to', 'priority', 'due_date')
        }),
        ('Organización', {
            'fields': ('labels', 'position', 'completed')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'task__title', 'author__username')
    readonly_fields = ('created_at',)
