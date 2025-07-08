# Trello Clone - Gestor de Tareas Colaborativo

Un sistema de gestión de tareas colaborativo inspirado en Trello, desarrollado con Django 4+ que permite organizar proyectos mediante tableros, listas y tareas con funcionalidad de arrastrar y soltar.

## 🚀 Características

### Funcionalidades Principales
- ✅ **Sistema de Autenticación**: Registro, login y logout de usuarios
- ✅ **Gestión de Tableros**: CRUD completo de tableros con control de acceso
- ✅ **Listas de Tareas**: Organización en columnas personalizables
- ✅ **Gestión de Tareas**: CRUD completo con asignación a usuarios
- ✅ **Drag & Drop**: Mover tareas entre listas con JavaScript vanilla
- ✅ **Prioridades y Etiquetas**: Sistema de clasificación de tareas
- ✅ **Fechas Límite**: Control de vencimientos con alertas visuales
- ✅ **Sistema de Comentarios**: Colaboración en tareas

### Características Avanzadas
- 📊 **Exportación**: Datos en formato CSV y JSON
- 📧 **Notificaciones**: Email automático para asignaciones y cambios
- 🔍 **Búsqueda**: Sistema de búsqueda global de tareas
- 📱 **Responsive**: Diseño adaptable a dispositivos móviles
- ⌨️ **Atajos de Teclado**: Navegación rápida
- 🎨 **Interfaz Moderna**: Diseño inspirado en Material Design

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 4.2.7
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Estilos**: Bootstrap 5.1.3
- **Iconos**: Font Awesome 6.0
- **Formularios**: Django Crispy Forms
- **Email**: Django SMTP Backend

## 📋 Requisitos del Sistema

- Python 3.8+
- Django 4.2+
- SQLite (incluido con Python) o PostgreSQL
- Navegador web moderno con soporte para ES6

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/trello-clone.git
cd trello-clone
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv

# En Linux/Mac
source venv/bin/activate

# En Windows
venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuración de Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-aplicacion
DEFAULT_FROM_EMAIL=noreply@trelloclone.com
```

### 5. Configurar Base de Datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 7. Cargar Datos de Prueba (Opcional)
```bash
python manage.py shell
```

Ejecutar en el shell de Django:
```python
from django.contrib.auth.models import User
from boards.models import Board, TaskList, Task

# Crear usuarios de prueba
user1 = User.objects.create_user('demo', 'demo@example.com', 'demo123')
user1.first_name = 'Usuario'
user1.last_name = 'Demo'
user1.save()

user2 = User.objects.create_user('colaborador', 'colab@example.com', 'colab123')
user2.first_name = 'Colaborador'
user2.last_name = 'Ejemplo'
user2.save()

# Crear tablero de ejemplo
board = Board.objects.create(
    name='Proyecto de Ejemplo',
    description='Un tablero de demostración con tareas de ejemplo',
    owner=user1
)
board.members.add(user2)

# Las listas se crean automáticamente por señal
todo_list = board.lists.get(name='Por hacer')
progress_list = board.lists.get(name='En progreso')
done_list = board.lists.get(name='Terminado')

# Crear tareas de ejemplo
Task.objects.create(
    title='Configurar entorno de desarrollo',
    description='Instalar Python, Django y dependencias necesarias',
    task_list=done_list,
    priority='H',
    assigned_to=user1,
    completed=True,
    labels='setup, desarrollo'
)

Task.objects.create(
    title='Diseñar modelos de datos',
    description='Crear modelos para Board, TaskList, Task y User',
    task_list=done_list,
    priority='H',
    assigned_to=user1,
    completed=True,
    labels='backend, modelos'
)

Task.objects.create(
    title='Implementar drag and drop',
    description='Añadir funcionalidad para mover tareas entre listas',
    task_list=progress_list,
    priority='M',
    assigned_to=user2,
    labels='frontend, javascript'
)

Task.objects.create(
    title='Añadir notificaciones por email',
    description='Enviar emails cuando se asignan o modifican tareas',
    task_list=todo_list,
    priority='L',
    assigned_to=user2,
    labels='email, notificaciones'
)

Task.objects.create(
    title='Implementar búsqueda de tareas',
    description='Sistema de búsqueda global por título, descripción y etiquetas',
    task_list=todo_list,
    priority='M',
    labels='búsqueda, frontend'
)

print("Datos de prueba creados exitosamente!")
print("Usuario demo: demo / demo123")
print("Usuario colaborador: colaborador / colab123")
```

### 8. Ejecutar Servidor de Desarrollo
```bash
python manage.py runserver
```

Visita `http://127.0.0.1:8000` en tu navegador.

## 📱 Uso de la Aplicación

### Primeros Pasos
1. **Registrarse**: Crear una cuenta nueva o usar las credenciales de prueba
2. **Crear Tablero**: Hacer clic en "Crear Tablero" desde la página principal
3. **Añadir Listas**: Usar el formulario "Añadir Lista" en el tablero
4. **Crear Tareas**: Usar el botón "+" en cada lista o "Nueva Tarea"
5. **Mover Tareas**: Arrastrar y soltar entre listas

### Funcionalidades Avanzadas
- **Asignar Tareas**: Editar tarea y seleccionar usuario asignado
- **Establecer Prioridades**: Usar el campo prioridad (Baja, Media, Alta, Crítica)
- **Añadir Etiquetas**: Separar múltiples etiquetas con comas
- **Comentarios**: Usar la sección de comentarios en el detalle de tarea
- **Exportar Datos**: Usar el menú "Exportar" en cada tablero

### Atajos de Teclado
- `N`: Crear nueva tarea (enfoca primer formulario)
- `L`: Crear nueva lista
- `F`: Enfocar búsqueda
- `Ctrl/Cmd + K`: Búsqueda rápida
- `Escape`: Cerrar modales y formularios

## 🧪 Ejecutar Tests

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests específicos
python manage.py test boards.tests.BoardModelTest

# Ejecutar con cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📊 Estructura del Proyecto

```
trello_clone/
├── manage.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
├── trello_clone/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── boards/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── signals.py
│   └── tests.py
├── templates/
│   ├── base.html
│   ├── registration/
│   └── boards/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       └── board.js
└── media/
```

## 🚀 Despliegue en Producción

### Preparación para Producción
1. **Configurar Variables de Entorno**:
```env
DEBUG=False
SECRET_KEY=clave-super-secreta-para-produccion
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=postgres://usuario:password@host:puerto/database
```

2. **Configurar Base de Datos PostgreSQL**:
```bash
pip install psycopg2-binary
```

3. **Recopilar Archivos Estáticos**:
```bash
python manage.py collectstatic
```

### Despliegue en Railway
1. Conectar repositorio GitHub a Railway
2. Configurar variables de entorno en Railway
3. Railway detectará automáticamente Django y desplegará

### Despliegue en Heroku
```bash
# Instalar Heroku CLI y crear app
heroku create tu-app-name

# Configurar variables de entorno
heroku config:set SECRET_KEY=tu-clave-secreta
heroku config:set DEBUG=False

# Desplegar
git push heroku main

# Ejecutar migraciones
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Despliegue en DigitalOcean Droplet
1. Crear droplet con Ubuntu 20.04
2. Instalar Python, PostgreSQL, Nginx
3. Configurar Gunicorn como servidor WSGI
4. Configurar Nginx como proxy reverso
5. Configurar SSL con Let's Encrypt

## 🔧 Configuración Avanzada

### Configuración de Email
Para habilitar notificaciones por email, configurar en `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

### Configuración de PostgreSQL
```python
# En settings.py para producción
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trello_clone_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Configuración de Redis (Cache)
```bash
pip install django-redis
```

```python
# En settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Guías de Contribución
- Seguir PEP 8 para código Python
- Añadir tests para nuevas funcionalidades
- Actualizar documentación cuando sea necesario
- Usar mensajes de commit descriptivos

## 🐛 Reportar Bugs

Usar GitHub Issues para reportar bugs. Incluir:
- Descripción detallada del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots si es aplicable
- Información del entorno (OS, navegador, versión Python)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Autores

- **Tu Nombre** - *Desarrollo inicial* - [tu-github](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Inspirado en [Trello](https://trello.com)
- Bootstrap para el framework CSS
- Font Awesome para los iconos
- Django community por el excelente framework

## 📞 Soporte

- **Email**: soporte@trelloclone.com
- **GitHub Issues**: [Crear issue](https://github.com/tu-usuario/trello-clone/issues)
- **Documentación**: [Wiki del proyecto](https://github.com/tu-usuario/trello-clone/wiki)

## 🔄 Changelog

### v1.0.0 (2024-01-XX)
- ✅ Sistema de autenticación completo
- ✅ CRUD de tableros, listas y tareas
- ✅ Drag and drop funcional
- ✅ Sistema de prioridades y etiquetas
- ✅ Exportación CSV/JSON
- ✅ Notificaciones por email
- ✅ Búsqueda global
- ✅ Diseño responsive
- ✅ Tests unitarios

## 🚧 Roadmap

### v1.1.0 (Próxima versión)
- [ ] API REST completa
- [ ] Aplicación móvil (React Native)
- [ ] Integración con calendarios
- [ ] Plantillas de tableros
- [ ] Modo oscuro
- [ ] Integración con Slack/Discord

### v1.2.0 (Futuro)
- [ ] Tableros públicos
- [ ] Sistema de roles avanzado
- [ ] Analíticas y reportes
- [ ] Integración con GitHub
- [ ] Automatizaciones (Zapier-like)
- [ ] Modo offline (PWA)
