#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Create a superuser if one doesn't exist"""
    if User.objects.filter(is_superuser=True).exists():
        print("Superuser already exists!")
        return

    try:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@riverside.com',
            password='admin123'
        )
        print(f"Superuser created successfully!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"Email: admin@riverside.com")

    except Exception as e:
        print(f"Error creating superuser: {e}")

if __name__ == '__main__':
    create_superuser()
