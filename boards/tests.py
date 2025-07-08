from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Board, TaskList, Task


class BoardModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.board = Board.objects.create(
            name='Test Board',
            description='Test Description',
            owner=self.user
        )

    def test_board_creation(self):
        self.assertEqual(self.board.name, 'Test Board')
        self.assertEqual(self.board.owner, self.user)
        self.assertTrue(self.board.created_at)

    def test_board_str_method(self):
        self.assertEqual(str(self.board), 'Test Board')

    def test_default_lists_creation(self):
        # Check if default lists are created via signal
        self.assertEqual(self.board.lists.count(), 3)
        list_names = list(self.board.lists.values_list('name', flat=True))
        self.assertIn('Por hacer', list_names)
        self.assertIn('En progreso', list_names)
        self.assertIn('Terminado', list_names)


class TaskListModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.board = Board.objects.create(
            name='Test Board',
            owner=self.user
        )
        self.task_list = TaskList.objects.create(
            name='Test List',
            board=self.board,
            position=0
        )

    def test_task_list_creation(self):
        self.assertEqual(self.task_list.name, 'Test List')
        self.assertEqual(self.task_list.board, self.board)
        self.assertEqual(self.task_list.position, 0)

    def test_task_list_str_method(self):
        expected = f"Test List ({self.board.name})"
        self.assertEqual(str(self.task_list), expected)


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.board = Board.objects.create(
            name='Test Board',
            owner=self.user
        )
        self.task_list = TaskList.objects.create(
            name='Test List',
            board=self.board
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            task_list=self.task_list,
            priority='H',
            labels='urgent, important'
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.task_list, self.task_list)
        self.assertEqual(self.task.priority, 'H')

    def test_task_str_method(self):
        self.assertEqual(str(self.task), 'Test Task')

    def test_priority_color_property(self):
        self.assertEqual(self.task.priority_color, 'danger')

    def test_labels_list_property(self):
        expected_labels = ['urgent', 'important']
        self.assertEqual(self.task.labels_list, expected_labels)


class BoardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.board = Board.objects.create(
            name='Test Board',
            owner=self.user
        )

    def test_board_list_view_requires_login(self):
        response = self.client.get(reverse('board_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_board_list_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('board_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Board')

    def test_board_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('board_detail', kwargs={'pk': self.board.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Board')

    def test_board_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('board_create'), {
            'name': 'New Board',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Board.objects.filter(name='New Board').exists())


class TaskViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.board = Board.objects.create(
            name='Test Board',
            owner=self.user
        )
        self.task_list = self.board.lists.first()  # Get one of the default lists
        self.task = Task.objects.create(
            title='Test Task',
            task_list=self.task_list
        )

    def test_task_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task_detail', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_task_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('task_create', kwargs={'board_pk': self.board.pk}), {
            'title': 'New Task',
            'description': 'New Description',
            'task_list': self.task_list.pk,
            'priority': 'M'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Task.objects.filter(title='New Task').exists())


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login


class ExportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.board = Board.objects.create(
            name='Test Board',
            owner=self.user
        )
        self.task_list = self.board.lists.first()
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            task_list=self.task_list,
            priority='H'
        )

    def test_csv_export(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('export_board_csv', kwargs={'pk': self.board.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('Test Task', response.content.decode())

    def test_json_export(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('export_board_json', kwargs={'pk': self.board.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
