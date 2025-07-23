"""
Django management command to reset demo data for River Side Food Court
Converts the init_demo_data.py script into a proper Django management command
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.contrib.auth.models import User
from vendors.models import Vendor, Category, MenuItem, Table
from orders.models import Order, OrderItem
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Reset all data to clean state for fresh demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset without confirmation prompt',
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write("🚀 Starting River Side Food Court Data Reset")
        self.stdout.write("="*50)

        # Show warning and get confirmation unless --force is used
        if not options['force']:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  WARNING: This will delete ALL orders and reset the system to clean state!\n"
                    "This action cannot be undone.\n"
                )
            )

            confirm = input("Are you sure you want to continue? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.ERROR("Operation cancelled."))
                return

        try:
            # Step 1: Clear all existing data
            self.clear_all_data()

            # Step 2: Ensure clean state
            self.ensure_clean_state()

            # Step 3: Verify clean state
            success = self.verify_clean_state()

            if success:
                self.stdout.write(
                    self.style.SUCCESS(
                        "\n🎉 Data reset completed successfully!\n"
                        "Your dashboard should now show:\n"
                        "   📊 Orders Today: 0\n"
                        "   💰 Unpaid Orders: 0\n"
                        "   🪑 Active Tables: 0\n"
                        "\nSystem is ready for fresh orders!"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING("\n⚠️  Data reset completed with warnings.")
                )

        except Exception as e:
            raise CommandError(f"Error during reset: {str(e)}")

    def clear_all_data(self):
        """Clear all orders and reset system to clean state"""
        self.stdout.write("🗑️  Clearing all data to reset state...")

        # Delete all orders (this will cascade to OrderItems)
        deleted_orders = Order.objects.all().delete()
        self.stdout.write(f"   Deleted {deleted_orders[0]} orders and related items")

        # Ensure we have standard tables (but no active orders)
        existing_tables = Table.objects.count()
        if existing_tables < 25:
            for i in range(existing_tables + 1, 26):
                Table.objects.create(
                    number=i,
                    seats=random.choice([2, 4, 6]),
                    is_active=True
                )
            self.stdout.write(f"   Created tables up to number 25")

        self.stdout.write("✅ System reset to clean state - all orders cleared")

    def ensure_clean_state(self):
        """Ensure system is in completely clean state"""
        self.stdout.write("🧹 Ensuring clean state...")

        # Verify no orders exist
        order_count = Order.objects.count()
        if order_count > 0:
            self.stdout.write(f"⚠️  Found {order_count} remaining orders, clearing...")
            Order.objects.all().delete()

        self.stdout.write("✅ System confirmed clean - no active orders")

    def verify_clean_state(self):
        """Verify the system is in clean state"""
        self.stdout.write("\n🔍 Verifying clean state...")

        today = timezone.now().date()

        # Check orders today
        orders_today = Order.objects.filter(created_at__date=today).count()
        self.stdout.write(f"📊 Orders Today: {orders_today}")

        # Check unpaid orders
        unpaid_orders = Order.objects.filter(status__in=['delivered', 'ready']).count()
        self.stdout.write(f"💰 Unpaid Orders: {unpaid_orders}")

        # Check active tables
        active_tables = Table.objects.filter(
            orders__status__in=['pending', 'confirmed', 'preparing']
        ).distinct().count()
        self.stdout.write(f"🪑 Active Tables: {active_tables}")

        # Check total orders
        total_orders = Order.objects.count()
        self.stdout.write(f"📦 Total Orders: {total_orders}")

        # Check available tables
        total_tables = Table.objects.filter(is_active=True).count()
        self.stdout.write(f"🪑 Available Tables: {total_tables}")

        self.stdout.write("\n🏪 Vendor Status:")
        for vendor in Vendor.objects.all():
            self.stdout.write(f"   {vendor.name}: Ready for orders")

        # Check if clean state is achieved
        is_clean = (
            orders_today == 0 and
            unpaid_orders == 0 and
            active_tables == 0 and
            total_orders == 0
        )

        if is_clean:
            self.stdout.write(
                self.style.SUCCESS(
                    "\n🎯 ✅ Clean state achieved successfully!\n"
                    "   📊 Orders Today: 0\n"
                    "   💰 Unpaid Orders: 0\n"
                    "   🪑 Active Tables: 0"
                )
            )
        else:
            self.stdout.write(self.style.ERROR("\n❌ Clean state not achieved."))

        return is_clean
