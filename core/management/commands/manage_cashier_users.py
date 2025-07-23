from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from django.db import transaction
from core.permissions import CashierPermissions, get_cashier_permission_summary
import getpass
from datetime import datetime

class Command(BaseCommand):
    help = 'Comprehensive cashier user management command'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Available actions')

        # List users
        list_parser = subparsers.add_parser('list', help='List all cashier users')
        list_parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed permission information'
        )

        # Add user
        add_parser = subparsers.add_parser('add', help='Add user to cashier group')
        add_parser.add_argument('username', help='Username to add')
        add_parser.add_argument('--create', action='store_true', help='Create user if not exists')
        add_parser.add_argument('--email', help='Email for new user')
        add_parser.add_argument('--first-name', help='First name for new user')
        add_parser.add_argument('--last-name', help='Last name for new user')

        # Remove user
        remove_parser = subparsers.add_parser('remove', help='Remove user from cashier group')
        remove_parser.add_argument('username', help='Username to remove')

        # Check permissions
        check_parser = subparsers.add_parser('check', help='Check user permissions')
        check_parser.add_argument('username', help='Username to check')

        # Audit
        audit_parser = subparsers.add_parser('audit', help='Audit all cashier users')
        audit_parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Automatically fix permission issues'
        )

        # Backup/Restore
        backup_parser = subparsers.add_parser('backup', help='Backup cashier user list')
        backup_parser.add_argument('--file', default='cashier_backup.txt', help='Backup file name')

        restore_parser = subparsers.add_parser('restore', help='Restore cashier users from backup')
        restore_parser.add_argument('file', help='Backup file to restore from')

    def handle(self, *args, **options):
        action = options.get('action')

        if not action:
            self.print_help()
            return

        try:
            if action == 'list':
                self.list_users(options)
            elif action == 'add':
                self.add_user(options)
            elif action == 'remove':
                self.remove_user(options)
            elif action == 'check':
                self.check_user(options)
            elif action == 'audit':
                self.audit_users(options)
            elif action == 'backup':
                self.backup_users(options)
            elif action == 'restore':
                self.restore_users(options)
            else:
                self.stdout.write(self.style.ERROR(f"Unknown action: {action}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

    def print_help(self):
        """Print usage help"""
        self.stdout.write("Cashier User Management Commands:")
        self.stdout.write("")
        self.stdout.write("  list [--detailed]              - List all cashier users")
        self.stdout.write("  add <username> [--create]      - Add user to cashier group")
        self.stdout.write("  remove <username>              - Remove user from cashier group")
        self.stdout.write("  check <username>               - Check user permissions")
        self.stdout.write("  audit [--fix-issues]           - Audit all cashier users")
        self.stdout.write("  backup [--file <name>]         - Backup cashier user list")
        self.stdout.write("  restore <file>                 - Restore from backup")
        self.stdout.write("")
        self.stdout.write("Examples:")
        self.stdout.write("  python manage.py manage_cashier_users list")
        self.stdout.write("  python manage.py manage_cashier_users add john --create --email john@restaurant.com")
        self.stdout.write("  python manage.py manage_cashier_users check john")

    def list_users(self, options):
        """List all cashier users"""
        try:
            cashier_group = Group.objects.get(name='Cashier')
            users = User.objects.filter(groups=cashier_group).order_by('username')

            self.stdout.write("👥 CASHIER USERS")
            self.stdout.write("=" * 50)

            if not users.exists():
                self.stdout.write("No cashier users found.")
                return

            for user in users:
                status_icon = "🟢" if user.is_active else "🔴"
                staff_badge = " [STAFF]" if user.is_staff else ""
                super_badge = " [SUPER]" if user.is_superuser else ""

                self.stdout.write(f"{status_icon} {user.username}{staff_badge}{super_badge}")
                self.stdout.write(f"   Name: {user.get_full_name() or 'Not set'}")
                self.stdout.write(f"   Email: {user.email or 'Not set'}")

                if user.last_login:
                    last_login = user.last_login.strftime('%Y-%m-%d %H:%M')
                else:
                    last_login = "Never"
                self.stdout.write(f"   Last login: {last_login}")

                if options.get('detailed'):
                    # Show permission status
                    status = CashierPermissions.check_cashier_permissions(user)
                    if status['has_all_permissions']:
                        self.stdout.write("   Permissions: ✅ Complete")
                    else:
                        missing_count = len(status['missing_permissions'])
                        self.stdout.write(f"   Permissions: ❌ Missing {missing_count}")

                self.stdout.write("")

        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR("Cashier group does not exist. Run setup_cashier_permissions first."))

    def add_user(self, options):
        """Add user to cashier group"""
        username = options['username']

        try:
            # Check if user exists
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f"Found existing user: {username}")
            except User.DoesNotExist:
                if options.get('create'):
                    user = self.create_user(username, options)
                else:
                    self.stdout.write(self.style.ERROR(f"User '{username}' not found. Use --create to create."))
                    return

            # Add to cashier group
            result = CashierPermissions.add_user_to_cashier_group(user)
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f"✅ {result['message']}"))

                # Show user summary
                self.show_user_summary(user)
            else:
                self.stdout.write(self.style.ERROR(f"❌ {result['message']}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error adding user: {str(e)}"))

    def create_user(self, username, options):
        """Create new user with provided options"""
        self.stdout.write(f"Creating new user: {username}")

        # Get password
        password = getpass.getpass('Enter password for new user: ')
        confirm_password = getpass.getpass('Confirm password: ')

        if password != confirm_password:
            raise ValueError("Passwords do not match")

        user = User.objects.create_user(
            username=username,
            email=options.get('email', ''),
            password=password,
            first_name=options.get('first_name', ''),
            last_name=options.get('last_name', ''),
        )

        self.stdout.write(self.style.SUCCESS(f"✅ Created user: {username}"))
        return user

    def remove_user(self, options):
        """Remove user from cashier group"""
        username = options['username']

        try:
            user = User.objects.get(username=username)

            if not CashierPermissions.is_cashier(user):
                self.stdout.write(self.style.WARNING(f"User '{username}' is not in cashier group"))
                return

            result = CashierPermissions.remove_user_from_cashier_group(user)
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f"✅ {result['message']}"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ {result['message']}"))

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found"))

    def check_user(self, options):
        """Check specific user permissions"""
        username = options['username']

        try:
            user = User.objects.get(username=username)
            summary = get_cashier_permission_summary(user)

            self.stdout.write("📋 USER PERMISSION REPORT")
            self.stdout.write("=" * 50)

            for key, value in summary.items():
                if key == 'missing_permissions' and value:
                    self.stdout.write(f"{key}: {len(value)} missing")
                    for perm in value:
                        self.stdout.write(f"   • {perm}")
                elif key == 'forbidden_permissions' and value:
                    self.stdout.write(f"{key}: {len(value)} security issues")
                    for perm in value:
                        self.stdout.write(f"   • {perm}")
                else:
                    self.stdout.write(f"{key}: {value}")

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found"))

    def audit_users(self, options):
        """Audit all cashier users for permission issues"""
        try:
            cashier_group = Group.objects.get(name='Cashier')
            users = User.objects.filter(groups=cashier_group)

            self.stdout.write("🔍 CASHIER USER AUDIT")
            self.stdout.write("=" * 50)

            issues_found = 0
            users_checked = 0

            for user in users:
                users_checked += 1
                status = CashierPermissions.check_cashier_permissions(user)

                user_issues = []

                # Check for missing permissions
                if not status['has_all_permissions']:
                    user_issues.append(f"Missing {len(status['missing_permissions'])} permissions")

                # Check for security issues
                if status['forbidden_permissions_held']:
                    user_issues.append(f"Has {len(status['forbidden_permissions_held'])} forbidden permissions")

                # Check account status
                if not user.is_active:
                    user_issues.append("Account inactive")

                if user_issues:
                    issues_found += len(user_issues)
                    self.stdout.write(f"❌ {user.username}:")
                    for issue in user_issues:
                        self.stdout.write(f"   • {issue}")

                    if options.get('fix_issues'):
                        self.fix_user_issues(user, status)
                else:
                    self.stdout.write(f"✅ {user.username}: No issues")

            self.stdout.write("")
            self.stdout.write(f"Audit complete: {users_checked} users checked, {issues_found} issues found")

        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR("Cashier group does not exist"))

    def fix_user_issues(self, user, status):
        """Attempt to fix user permission issues"""
        if not status['has_all_permissions']:
            # Re-add user to cashier group to refresh permissions
            result = CashierPermissions.add_user_to_cashier_group(user)
            if result['success']:
                self.stdout.write(f"   🔧 Fixed permissions for {user.username}")

    def backup_users(self, options):
        """Backup cashier user list"""
        filename = options.get('file', 'cashier_backup.txt')

        try:
            cashier_group = Group.objects.get(name='Cashier')
            users = User.objects.filter(groups=cashier_group)

            with open(filename, 'w') as f:
                f.write(f"# Cashier Users Backup - {datetime.now().isoformat()}\n")
                f.write("# Format: username,email,first_name,last_name,is_active,is_staff\n")

                for user in users:
                    f.write(f"{user.username},{user.email},{user.first_name},{user.last_name},{user.is_active},{user.is_staff}\n")

            self.stdout.write(self.style.SUCCESS(f"✅ Backed up {users.count()} users to {filename}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Backup failed: {str(e)}"))

    def restore_users(self, options):
        """Restore cashier users from backup"""
        filename = options['file']

        try:
            with open(filename, 'r') as f:
                lines = f.readlines()

            restored = 0
            for line in lines:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue

                parts = line.split(',')
                if len(parts) >= 6:
                    username, email, first_name, last_name, is_active, is_staff = parts[:6]

                    # Create user if doesn't exist
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'is_active': is_active.lower() == 'true',
                            'is_staff': is_staff.lower() == 'true'
                        }
                    )

                    # Add to cashier group
                    CashierPermissions.add_user_to_cashier_group(user)
                    restored += 1

            self.stdout.write(self.style.SUCCESS(f"✅ Restored {restored} users from {filename}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Backup file '{filename}' not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Restore failed: {str(e)}"))

    def show_user_summary(self, user):
        """Show user summary after operations"""
        self.stdout.write("")
        self.stdout.write("👤 USER SUMMARY")
        self.stdout.write("-" * 30)
        self.stdout.write(f"Username: {user.username}")
        self.stdout.write(f"Email: {user.email or 'Not set'}")
        self.stdout.write(f"Name: {user.get_full_name() or 'Not set'}")
        self.stdout.write(f"Active: {'Yes' if user.is_active else 'No'}")
        self.stdout.write(f"Groups: {', '.join(g.name for g in user.groups.all())}")

        # Permission status
        status = CashierPermissions.check_cashier_permissions(user)
        if status['has_all_permissions']:
            self.stdout.write("Permissions: ✅ Complete")
        else:
            self.stdout.write(f"Permissions: ❌ Missing {len(status['missing_permissions'])}")
