#!/usr/bin/env python3
"""
Setup script for Trello Clone Django application
This script helps users set up the project quickly
"""

import os
import sys
import subprocess
import secrets
import string

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Error output: {e.stderr}")
        return None

def generate_secret_key():
    """Generate a random secret key for Django"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for i in range(50))

def create_env_file():
    """Create .env file with default configuration"""
    if os.path.exists('.env'):
        print("📄 .env file already exists, skipping creation")
        return
    
    secret_key = generate_secret_key()
    env_content = f"""# Django Configuration
SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (SQLite by default)
# For PostgreSQL, uncomment and configure:
# DATABASE_URL=postgres://username:password@localhost:5432/trello_clone_db

# Email Configuration (Optional - for notifications)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=noreply@trelloclone.com
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with default configuration")

def main():
    """Main setup function"""
    print("🚀 Setting up Trello Clone Django Application")
    print("=" * 50)
    
    # Check if Python is available
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment
    if not os.path.exists('venv'):
        run_command('python -m venv venv', 'Creating virtual environment')
    else:
        print("📁 Virtual environment already exists")
    
    # Determine activation command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = 'venv\\Scripts\\activate'
        pip_cmd = 'venv\\Scripts\\pip'
        python_cmd = 'venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        activate_cmd = 'source venv/bin/activate'
        pip_cmd = 'venv/bin/pip'
        python_cmd = 'venv/bin/python'
    
    # Install dependencies
    run_command(f'{pip_cmd} install --upgrade pip', 'Upgrading pip')
    run_command(f'{pip_cmd} install -r requirements.txt', 'Installing dependencies')
    
    # Create .env file
    create_env_file()
    
    # Run Django setup commands
    run_command(f'{python_cmd} manage.py makemigrations', 'Creating database migrations')
    run_command(f'{python_cmd} manage.py migrate', 'Applying database migrations')
    
    # Ask if user wants to create sample data
    create_sample = input("\n🎯 Do you want to create sample data? (y/N): ").lower().strip()
    if create_sample in ['y', 'yes']:
        run_command(f'{python_cmd} manage.py create_sample_data', 'Creating sample data')
        print("\n📋 Sample data created with the following users:")
        print("   - admin / demo123 (superuser)")
        print("   - maria_garcia / demo123")
        print("   - juan_lopez / demo123")
    else:
        # Create superuser
        print("\n👤 Creating superuser account...")
        print("Please follow the prompts to create an admin account:")
        subprocess.run(f'{python_cmd} manage.py createsuperuser', shell=True)
    
    # Collect static files
    run_command(f'{python_cmd} manage.py collectstatic --noinput', 'Collecting static files')
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print(f"   1. Activate virtual environment: {activate_cmd}")
    print(f"   2. Start development server: {python_cmd} manage.py runserver")
    print("   3. Open http://127.0.0.1:8000 in your browser")
    print("\n📚 Additional commands:")
    print(f"   - Run tests: {python_cmd} manage.py test")
    print(f"   - Create more sample data: {python_cmd} manage.py create_sample_data")
    print(f"   - Access admin panel: http://127.0.0.1:8000/admin/")
    
    if create_sample in ['y', 'yes']:
        print("\n🔑 You can login with any of the sample users listed above")
    
    print("\n📖 For more information, check the README.md file")

if __name__ == '__main__':
    main()
