from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.db import transaction

class Command(BaseCommand):
    help = 'Create a cashier user with appropriate permissions'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the cashier')
        parser.add_argument('--email', type=str, help='Email for the cashier')
        parser.add_argument('--password', type=str, help='Password for the cashier')
        parser.add_argument('--staff', action='store_true', help='Make user staff (can access admin)')
        parser.add_argument('--superuser', action='store_true', help='Make user superuser (full admin access)')

    def handle(self, *args, **options):
        username = options['username']
        email = options.get('email', f'{username}@restaurant.com')
        password = options.get('password', 'cashier123')
        is_staff = options.get('staff', True)
        is_superuser = options.get('superuser', False)

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User "{username}" already exists')
            )
            return

        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_staff=is_staff,
                    is_superuser=is_superuser
                )

                # Get or create Cashiers group
                cashiers_group, created = Group.objects.get_or_create(name='Cashiers')

                # Add user to Cashiers group
                user.groups.add(cashiers_group)

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created cashier user: {username}')
                )
                self.stdout.write(f'Email: {email}')
                self.stdout.write(f'Password: {password}')
                self.stdout.write(f'Staff Access: {is_staff}')
                self.stdout.write(f'Superuser: {is_superuser}')
                self.stdout.write(f'Groups: Cashiers')

                self.stdout.write('\n' + self.style.WARNING('NEXT STEPS:'))
                self.stdout.write('1. Login at /admin/ with these credentials')
                self.stdout.write('2. Access cashier dashboard at /cashier/')
                self.stdout.write('3. Change password on first login')

                if not is_superuser:
                    self.stdout.write('4. Grant additional permissions in admin if needed')

        except Exception as e:
            raise CommandError(f'Error creating cashier user: {e}')
