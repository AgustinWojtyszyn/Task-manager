from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Board, TaskList, Task, TaskComment


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'username',
            'email',
            'password1',
            'password2',
            Submit('submit', 'Registrarse', css_class='btn btn-primary btn-block')
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'description', 'members']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'members': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Exclude the current user from members selection
            self.fields['members'].queryset = User.objects.exclude(id=user.id)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            Field('members', css_class='form-check'),
            Submit('submit', 'Guardar Tablero', css_class='btn btn-primary')
        )


class TaskListForm(forms.ModelForm):
    class Meta:
        model = TaskList
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-8 mb-0'),
                Column(Submit('submit', 'Añadir Lista', css_class='btn btn-success'), css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            )
        )


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'labels', 'assigned_to', 'task_list']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if board:
            self.fields['task_list'].queryset = TaskList.objects.filter(board=board)
            # Include board members and owner in assigned_to options
            board_users = User.objects.filter(
                models.Q(owned_boards=board) | models.Q(boards=board)
            ).distinct()
            self.fields['assigned_to'].queryset = board_users
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            Row(
                Column('task_list', css_class='form-group col-md-6 mb-0'),
                Column('assigned_to', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('priority', css_class='form-group col-md-4 mb-0'),
                Column('due_date', css_class='form-group col-md-4 mb-0'),
                Column('labels', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Guardar Tarea', css_class='btn btn-primary')
        )


class QuickTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'placeholder': 'Añadir una tarea...',
            'class': 'form-control'
        })


class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Añadir un comentario...'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'content',
            Submit('submit', 'Añadir Comentario', css_class='btn btn-primary btn-sm')
        )


class TaskMoveForm(forms.Form):
    new_list = forms.ModelChoiceField(queryset=TaskList.objects.none())
    new_position = forms.IntegerField(min_value=0, required=False)

    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        
        if board:
            self.fields['new_list'].queryset = TaskList.objects.filter(board=board)
