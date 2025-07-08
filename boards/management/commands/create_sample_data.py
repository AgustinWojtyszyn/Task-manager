from django.core.management.base import BaseCommand  # Corregido el import
from django.contrib.auth.models import User
from boards.models import Board, TaskList, Task, TaskComment
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample data for testing the Trello Clone application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=3,
            help='Number of users to create (default: 3)'
        )
        parser.add_argument(
            '--boards',
            type=int,
            default=2,
            help='Number of boards to create (default: 2)'
        )
        parser.add_argument(
            '--tasks',
            type=int,
            default=15,
            help='Number of tasks to create (default: 15)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Crear usuarios
        users = self.create_users(options['users'])
        self.stdout.write(f'Created {len(users)} users')

        # Crear tableros
        boards = self.create_boards(users, options['boards'])
        self.stdout.write(f'Created {len(boards)} boards')

        # Crear listas para cada tablero si no existen
        for board in boards:
            if board.lists.count() == 0:
                for list_name in ['Por hacer', 'En progreso', 'Terminado']:
                    TaskList.objects.create(name=list_name, board=board)

        # Crear tareas
        tasks = self.create_tasks(users, boards, options['tasks'])
        self.stdout.write(f'Created {len(tasks)} tasks')

        # Crear comentarios
        comments = self.create_comments(users, tasks)
        self.stdout.write(f'Created {len(comments)} comments')

        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )
        
        # Imprimir credenciales de acceso
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.WARNING('LOGIN CREDENTIALS:'))
        self.stdout.write('='*50)
        for user in users:
            self.stdout.write(f'Username: {user.username} | Password: demo123')
        self.stdout.write('='*50)

    def create_users(self, count):
        users = []
        user_data = [
            ('admin', 'Admin', 'User', 'admin@trelloclone.com'),
            ('maria_garcia', 'María', 'García', 'maria@example.com'),
            ('juan_lopez', 'Juan', 'López', 'juan@example.com'),
            ('ana_martinez', 'Ana', 'Martínez', 'ana@example.com'),
            ('carlos_rodriguez', 'Carlos', 'Rodríguez', 'carlos@example.com'),
        ]

        for i in range(min(count, len(user_data))):
            username, first_name, last_name, email = user_data[i]
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'is_staff': username == 'admin',
                    'is_superuser': username == 'admin',
                }
            )
            
            if created:
                user.set_password('demo123')
                user.save()
                self.stdout.write(f'  Created user: {username}')
            else:
                self.stdout.write(f'  User already exists: {username}')
            
            users.append(user)

        return users

    def create_boards(self, users, count):
        boards = []
        board_data = [
            {
                'name': 'Desarrollo de Aplicación Web',
                'description': 'Proyecto para desarrollar una aplicación web moderna con Django y React'
            },
            {
                'name': 'Campaña de Marketing Digital',
                'description': 'Planificación y ejecución de campaña de marketing para el lanzamiento del producto'
            },
            {
                'name': 'Rediseño de Sitio Web',
                'description': 'Modernización completa del sitio web corporativo con nuevo diseño UX/UI'
            },
            {
                'name': 'Migración a la Nube',
                'description': 'Migración de infraestructura local a servicios en la nube (AWS/Azure)'
            },
            {
                'name': 'Proyecto de Investigación',
                'description': 'Investigación de nuevas tecnologías y tendencias del mercado'
            }
        ]

        for i in range(min(count, len(board_data))):
            data = board_data[i]
            owner = random.choice(users)
            
            board = Board.objects.create(
                name=data['name'],
                description=data['description'],
                owner=owner
            )
            
            # Añadir miembros aleatorios
            members = random.sample(users, random.randint(1, min(3, len(users))))
            for member in members:
                if member != owner:
                    board.members.add(member)
            
            boards.append(board)
            self.stdout.write(f'  Created board: {board.name}')

        return boards

    def create_tasks(self, users, boards, count):
        tasks = []
        task_templates = [
            # Development tasks
            {
                'title': 'Configurar entorno de desarrollo',
                'description': 'Instalar y configurar todas las herramientas necesarias para el desarrollo',
                'priority': 'H',
                'labels': 'setup, desarrollo, configuración'
            },
            {
                'title': 'Diseñar base de datos',
                'description': 'Crear el esquema de base de datos y las relaciones entre entidades',
                'priority': 'H',
                'labels': 'database, diseño, backend'
            },
            {
                'title': 'Implementar autenticación',
                'description': 'Sistema de login, registro y gestión de usuarios',
                'priority': 'H',
                'labels': 'auth, seguridad, backend'
            },
            {
                'title': 'Crear API REST',
                'description': 'Desarrollar endpoints para la comunicación frontend-backend',
                'priority': 'M',
                'labels': 'api, backend, rest'
            },
            {
                'title': 'Diseñar interfaz de usuario',
                'description': 'Crear mockups y prototipos de la interfaz de usuario',
                'priority': 'M',
                'labels': 'ui, diseño, frontend'
            },
            {
                'title': 'Implementar drag and drop',
                'description': 'Funcionalidad para arrastrar y soltar elementos en la interfaz',
                'priority': 'M',
                'labels': 'frontend, javascript, ux'
            },
            {
                'title': 'Optimizar rendimiento',
                'description': 'Mejorar la velocidad de carga y respuesta de la aplicación',
                'priority': 'L',
                'labels': 'performance, optimización'
            },
            {
                'title': 'Escribir documentación',
                'description': 'Documentar el código y crear guías de usuario',
                'priority': 'L',
                'labels': 'documentación, manual'
            },
            {
                'title': 'Configurar CI/CD',
                'description': 'Automatizar el proceso de integración y despliegue continuo',
                'priority': 'M',
                'labels': 'devops, ci/cd, automatización'
            },
            {
                'title': 'Implementar tests unitarios',
                'description': 'Crear suite de tests para asegurar la calidad del código',
                'priority': 'M',
                'labels': 'testing, calidad, backend'
            },
            # Marketing tasks
            {
                'title': 'Análisis de mercado',
                'description': 'Investigar competencia y tendencias del mercado objetivo',
                'priority': 'H',
                'labels': 'investigación, mercado, análisis'
            },
            {
                'title': 'Crear contenido para redes sociales',
                'description': 'Desarrollar estrategia de contenido para Facebook, Instagram y Twitter',
                'priority': 'M',
                'labels': 'social media, contenido, marketing'
            },
            {
                'title': 'Diseñar campaña publicitaria',
                'description': 'Crear anuncios para Google Ads y Facebook Ads',
                'priority': 'M',
                'labels': 'publicidad, ads, diseño'
            },
            {
                'title': 'Optimizar SEO',
                'description': 'Mejorar el posicionamiento en motores de búsqueda',
                'priority': 'L',
                'labels': 'seo, optimización, web'
            },
            {
                'title': 'Analizar métricas',
                'description': 'Revisar KPIs y métricas de rendimiento de las campañas',
                'priority': 'L',
                'labels': 'analytics, métricas, kpi'
            }
        ]

        # Distribuir tareas entre tableros
        tasks_per_board = count // len(boards)
        remaining_tasks = count % len(boards)

        for board in boards:
            # Obtener listas para este tablero
            lists = list(board.lists.all())
            if not lists:
                # Si no hay listas, crearlas
                for list_name in ['Por hacer', 'En progreso', 'Terminado']:
                    TaskList.objects.create(name=list_name, board=board)
                lists = list(board.lists.all())
            
            # Número de tareas para este tablero
            board_task_count = tasks_per_board
            if remaining_tasks > 0:
                board_task_count += 1
                remaining_tasks -= 1

            for i in range(board_task_count):
                template = random.choice(task_templates)
                task_list = random.choice(lists)
                assigned_user = random.choice([None] + list(board.members.all()) + [board.owner])
                
                # Fecha de vencimiento aleatoria (algunas tareas sin fecha)
                due_date = None
                if random.choice([True, False]):
                    days_ahead = random.randint(1, 30)
                    due_date = date.today() + timedelta(days=days_ahead)

                # Estado de completado aleatorio
                completed = random.choice([True, False]) if task_list.name == 'Terminado' else False

                task = Task.objects.create(
                    title=template['title'],
                    description=template['description'],
                    task_list=task_list,
                    priority=template['priority'],
                    labels=template['labels'],
                    assigned_to=assigned_user,
                    due_date=due_date,
                    completed=completed
                )
                
                tasks.append(task)

        return tasks

    def create_comments(self, users, tasks):
        comments = []
        comment_templates = [
            "Excelente trabajo en esta tarea. ¿Podrías añadir más detalles sobre la implementación?",
            "He revisado el código y todo se ve bien. Listo para merge.",
            "Necesitamos discutir algunos aspectos de esta funcionalidad en la próxima reunión.",
            "¿Hay algún bloqueador para completar esta tarea?",
            "Actualicé los requisitos. Por favor, revisa los cambios.",
            "Esta tarea está relacionada con el ticket #123. Hay que coordinar.",
            "Buen progreso. ¿Cuándo estimas que estará terminado?",
            "He encontrado un bug menor. Lo documenté en los comentarios del código.",
            "La funcionalidad está funcionando correctamente en mi entorno de pruebas.",
            "¿Podemos programar una demo de esta funcionalidad para el cliente?"
        ]

        # Añadir comentarios a tareas aleatorias
        if not tasks:
            return comments

        sample_size = min(len(tasks), max(1, len(tasks) // 2))
        for task in random.sample(tasks, sample_size):
            num_comments = random.randint(1, 3)
            
            for _ in range(num_comments):
                author = random.choice(users)
                content = random.choice(comment_templates)
                
                comment = TaskComment.objects.create(
                    task=task,
                    author=author,
                    content=content
                )
                
                comments.append(comment)

        return comments
