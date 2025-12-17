"""
Management command to set up default users for the Labour Management System
Usage: python manage.py setup_users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates default Supervisor and Admin users'

    def handle(self, *args, **kwargs):
        # Create Supervisor user: ngenes / super
        supervisor, created = User.objects.get_or_create(
            username='ngenes',
            defaults={
                'email': 'supervisor@company.com',
                'is_staff': True,
                'is_superuser': False,
                'first_name': 'Supervisor',
                'last_name': 'Ngenes'
            }
        )
        
        if created:
            supervisor.set_password('super')
            supervisor.save()
            self.stdout.write(self.style.SUCCESS('✓ Created Supervisor user: ngenes'))
        else:
            # Update password even if user exists
            supervisor.set_password('super')
            supervisor.is_staff = True
            supervisor.is_superuser = False
            supervisor.save()
            self.stdout.write(self.style.WARNING('⚠ Supervisor user "ngenes" already exists - password updated'))
        
        # Create Admin user: Burita / admin23
        admin, created = User.objects.get_or_create(
            username='Burita',
            defaults={
                'email': 'admin@company.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'Burita'
            }
        )
        
        if created:
            admin.set_password('admin23')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✓ Created Admin user: Burita'))
        else:
            # Update password even if user exists
            admin.set_password('admin23')
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.WARNING('⚠ Admin user "Burita" already exists - password updated'))
        
        self.stdout.write(self.style.SUCCESS('\n=== User Setup Complete ==='))
        self.stdout.write('Supervisor Login: ngenes / super')
        self.stdout.write('Admin Login: Burita / admin23')
