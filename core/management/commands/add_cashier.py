from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from django.db import transaction
import getpass

class Command(BaseCommand):
    help = 'Add a user to the Cashier group or create a new cashier user'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='Username of the user to add to Cashier group'
        )
        parser.add_argument(
            '--create',
            action='store_true',
            help='Create a new user if username does not exist',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for new user (only used with --create)',
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='First name for new user (only used with --create)',
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Last name for new user (only used with --create)',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for new user (will prompt if not provided with --create)',
        )

    def handle(self, *args, **options):
        username = options['username']

        try:
            with transaction.atomic():
                # Get or create cashier group
                cashier_group, created = Group.objects.get_or_create(name='Cashier')
                if created:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Created Cashier group')
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            '⚠️  Please run "python manage.py setup_cashier_permissions" to set up permissions'
                        )
                    )

                # Try to get existing user
                try:
                    user = User.objects.get(username=username)
                    self.stdout.write(f"✅ Found existing user: {username}")

                except User.DoesNotExist:
                    if options['create']:
                        user = self.create_new_user(username, options)
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"❌ User '{username}' not found. Use --create to create a new user."
                            )
                        )
                        return

                # Add user to cashier group
                if cashier_group in user.groups.all():
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  User '{username}' is already in Cashier group")
                    )
                else:
                    user.groups.add(cashier_group)
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Added '{username}' to Cashier group")
                    )

                # Show user summary
                self.show_user_summary(user)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error: {str(e)}")
            )

    def create_new_user(self, username, options):
        """Create a new user with the provided information"""
        self.stdout.write(f"🔨 Creating new user: {username}")

        # Get password
        password = options.get('password')
        if not password:
            password = getpass.getpass('Enter password for new user: ')
            confirm_password = getpass.getpass('Confirm password: ')
            if password != confirm_password:
                raise ValueError("Passwords do not match")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=options.get('email', ''),
            password=password,
            first_name=options.get('first_name', ''),
            last_name=options.get('last_name', ''),
        )

        self.stdout.write(
            self.style.SUCCESS(f"✅ Created new user: {username}")
        )

        return user

    def show_user_summary(self, user):
        """Show a summary of the user's information and permissions"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("👤 USER SUMMARY")
        self.stdout.write("="*50)

        self.stdout.write(f"Username: {user.username}")
        self.stdout.write(f"Full Name: {user.get_full_name() or 'Not set'}")
        self.stdout.write(f"Email: {user.email or 'Not set'}")
        self.stdout.write(f"Active: {'Yes' if user.is_active else 'No'}")
        self.stdout.write(f"Staff Status: {'Yes' if user.is_staff else 'No'}")
        self.stdout.write(f"Superuser: {'Yes' if user.is_superuser else 'No'}")

        # Show groups
        groups = user.groups.all()
        if groups:
            self.stdout.write(f"Groups: {', '.join(group.name for group in groups)}")
        else:
            self.stdout.write("Groups: None")

        # Show last login
        if user.last_login:
            self.stdout.write(f"Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.stdout.write("Last Login: Never")

        # Show cashier capabilities
        self.stdout.write("\n🎯 CASHIER CAPABILITIES:")
        capabilities = [
            "✅ Access cashier dashboard at /cashier/",
            "✅ View and process orders",
            "✅ Mark orders as paid",
            "✅ Reset tables",
            "✅ View sales reports",
            "✅ View vendor information",
        ]

        for capability in capabilities:
            self.stdout.write(f"   {capability}")

        # Show login instructions
        self.stdout.write("\n🚪 LOGIN INSTRUCTIONS:")
        self.stdout.write(f"   1. Go to your site's cashier login page")
        self.stdout.write(f"   2. Use username: {user.username}")
        self.stdout.write(f"   3. Use the password you just set")
        self.stdout.write(f"   4. You'll be redirected to the cashier dashboard")

        # Show next steps
        self.stdout.write("\n📋 NEXT STEPS:")
        next_steps = [
            "1. Ensure cashier permissions are set up: python manage.py setup_cashier_permissions",
            "2. Test login at the cashier dashboard",
            "3. Verify user can process payments and manage orders",
            "4. Train user on cashier system procedures",
        ]

        for step in next_steps:
            self.stdout.write(f"   {step}")
