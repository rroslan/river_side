from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set up proper permissions for the Cashier group'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset cashier permissions (remove and recreate)',
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='List all users in the Cashier group',
        )

    def handle(self, *args, **options):
        if options['list_users']:
            self.list_cashier_users()
            return

        try:
            with transaction.atomic():
                cashier_group = self.setup_cashier_group(reset=options['reset'])
                self.assign_permissions(cashier_group)
                self.verify_permissions(cashier_group)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Successfully set up permissions for Cashier group'
                    )
                )

                # Show summary
                self.show_permission_summary(cashier_group)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up cashier permissions: {str(e)}')
            )
            logger.error(f'Error in setup_cashier_permissions: {str(e)}')

    def setup_cashier_group(self, reset=False):
        """Create or get the Cashier group"""
        try:
            cashier_group = Group.objects.get(name='Cashier')
            if reset:
                self.stdout.write("🔄 Resetting existing Cashier group permissions...")
                cashier_group.permissions.clear()
            else:
                self.stdout.write("✅ Found existing Cashier group")
        except Group.DoesNotExist:
            cashier_group = Group.objects.create(name='Cashier')
            self.stdout.write("✅ Created new Cashier group")

        return cashier_group

    def assign_permissions(self, cashier_group):
        """Assign all necessary permissions to the cashier group"""

        # Define permissions needed for cashiers
        permission_mappings = [
            # Orders app permissions
            ('orders', 'order', ['view', 'change']),
            ('orders', 'orderitem', ['view', 'change']),
            ('orders', 'orderstatushistory', ['view', 'add']),
            ('orders', 'cart', ['view', 'change', 'delete']),
            ('orders', 'cartitem', ['view', 'change', 'delete']),

            # Vendors app permissions
            ('vendors', 'vendor', ['view']),
            ('vendors', 'category', ['view']),
            ('vendors', 'menuitem', ['view']),
            ('vendors', 'table', ['view', 'change']),

            # Auth permissions (limited)
            ('auth', 'user', ['view']),
            ('auth', 'group', ['view']),
        ]

        assigned_count = 0

        for app_label, model_name, actions in permission_mappings:
            try:
                content_type = ContentType.objects.get(
                    app_label=app_label,
                    model=model_name
                )

                for action in actions:
                    codename = f"{action}_{model_name}"
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type=content_type
                        )
                        cashier_group.permissions.add(permission)
                        assigned_count += 1
                        self.stdout.write(f"  ✅ Added: {app_label}.{codename}")
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠️  Permission not found: {app_label}.{codename}"
                            )
                        )

            except ContentType.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠️  ContentType not found: {app_label}.{model_name}"
                    )
                )

        self.stdout.write(f"📋 Assigned {assigned_count} permissions to Cashier group")

    def verify_permissions(self, cashier_group):
        """Verify that all expected permissions are assigned"""
        expected_permissions = [
            'orders.view_order',
            'orders.change_order',
            'orders.view_orderitem',
            'orders.change_orderitem',
            'orders.view_orderstatushistory',
            'orders.add_orderstatushistory',
            'vendors.view_vendor',
            'vendors.view_category',
            'vendors.view_menuitem',
            'vendors.view_table',
            'vendors.change_table',
        ]

        assigned_permissions = [
            f"{perm.content_type.app_label}.{perm.codename}"
            for perm in cashier_group.permissions.all()
        ]

        self.stdout.write("\n🔍 Verifying permissions:")

        for perm in expected_permissions:
            if perm in assigned_permissions:
                self.stdout.write(f"  ✅ {perm}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ❌ Missing: {perm}")
                )

    def show_permission_summary(self, cashier_group):
        """Show a summary of what cashiers can do"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📋 CASHIER PERMISSIONS SUMMARY")
        self.stdout.write("="*60)

        permissions_by_app = {}
        for perm in cashier_group.permissions.all():
            app = perm.content_type.app_label
            if app not in permissions_by_app:
                permissions_by_app[app] = []
            permissions_by_app[app].append(f"{perm.codename}")

        for app, perms in permissions_by_app.items():
            self.stdout.write(f"\n🏷️  {app.upper()} App:")
            for perm in sorted(perms):
                self.stdout.write(f"   • {perm}")

        # Show functional capabilities
        self.stdout.write("\n🎯 CASHIER CAPABILITIES:")
        capabilities = [
            "✅ View and manage orders",
            "✅ Process payments (mark orders as paid)",
            "✅ View order history and status",
            "✅ Reset tables (cancel pending orders)",
            "✅ View vendor and menu information",
            "✅ Access cashier dashboard",
            "✅ View sales reports and statistics",
            "❌ Cannot create/delete orders",
            "❌ Cannot modify menu items or prices",
            "❌ Cannot create users or modify permissions",
            "❌ Cannot access Django admin for restricted models",
        ]

        for capability in capabilities:
            self.stdout.write(f"   {capability}")

        # Show user count
        user_count = User.objects.filter(groups=cashier_group).count()
        self.stdout.write(f"\n👥 Current users in Cashier group: {user_count}")

    def list_cashier_users(self):
        """List all users in the Cashier group"""
        try:
            cashier_group = Group.objects.get(name='Cashier')
            users = User.objects.filter(groups=cashier_group)

            self.stdout.write("👥 CASHIER GROUP USERS")
            self.stdout.write("="*40)

            if users.exists():
                for user in users:
                    status = "🟢 Active" if user.is_active else "🔴 Inactive"
                    last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "Never"
                    self.stdout.write(f"• {user.username} ({user.get_full_name() or 'No name'}) - {status}")
                    self.stdout.write(f"  Last login: {last_login}")
                    self.stdout.write(f"  Email: {user.email or 'No email'}")
                    self.stdout.write("")
            else:
                self.stdout.write("No users found in Cashier group")

        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ Cashier group does not exist. Run without --list-users first.")
            )

    def add_user_to_cashier_group(self, username):
        """Helper method to add a user to cashier group"""
        try:
            user = User.objects.get(username=username)
            cashier_group = Group.objects.get(name='Cashier')
            user.groups.add(cashier_group)
            self.stdout.write(
                self.style.SUCCESS(f"✅ Added {username} to Cashier group")
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ User {username} not found")
            )
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ Cashier group not found. Run setup first.")
            )
