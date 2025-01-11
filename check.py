import os
import django

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salesMs.settings')  # Replace 'salesMs' with your project name

# Initialize Django
django.setup()

from django.contrib.auth.models import Group

# Your script logic here
required_groups = ['Agent', 'admin']
for group_name in required_groups:
    if not Group.objects.filter(name=group_name).exists():
        Group.objects.create(name=group_name)
        print(f"Group '{group_name}' created.")
