#!/usr/bin/env python
"""
Demo Data Reset Script for River Side Food Court
Resets all data to clean state for fresh demonstration:
- Orders Today: 0
- Unpaid Orders: 0
- Active Tables: 0
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from vendors.models import Vendor, Category, MenuItem, Table
from orders.models import Order, OrderItem

def clear_all_data():
    """Clear all orders and reset system to clean state"""
    print("🗑️  Clearing all data to reset state...")

    # Delete all orders (this will cascade to OrderItems)
    deleted_orders = Order.objects.all().delete()
    print(f"   Deleted {deleted_orders[0]} orders and related items")

    # Ensure we have standard tables (but no active orders)
    existing_tables = Table.objects.count()
    if existing_tables < 25:
        for i in range(existing_tables + 1, 26):
            Table.objects.create(
                number=i,
                seats=random.choice([2, 4, 6]),
                is_active=True
            )
        print(f"   Created tables up to number 25")

    print("✅ System reset to clean state - all orders cleared")

def get_random_items(vendor=None, count=3):
    """Get random menu items, optionally from specific vendor"""
    if vendor:
        items = MenuItem.objects.filter(
            category__vendor=vendor,
            is_available=True
        )
    else:
        items = MenuItem.objects.filter(is_available=True)

    if items.count() == 0:
        return []

    return random.sample(list(items), min(count, items.count()))

def calculate_order_total(items_data):
    """Calculate total for order items"""
    total = Decimal('0.00')
    for item, quantity in items_data:
        total += item.price * quantity
    return total

def ensure_clean_state():
    """Ensure system is in completely clean state"""
    print("🧹 Ensuring clean state...")

    # Verify no orders exist
    order_count = Order.objects.count()
    if order_count > 0:
        print(f"⚠️  Found {order_count} remaining orders, clearing...")
        Order.objects.all().delete()

    print("✅ System confirmed clean - no active orders")
    return []

def verify_clean_state():
    """Verify the system is in clean state"""
    print("\n🔍 Verifying clean state...")

    today = timezone.now().date()

    # Check orders today
    orders_today = Order.objects.filter(created_at__date=today).count()
    print(f"📊 Orders Today: {orders_today}")

    # Check unpaid orders
    unpaid_orders = Order.objects.filter(status__in=['delivered', 'ready']).count()
    print(f"💰 Unpaid Orders: {unpaid_orders}")

    # Check active tables
    active_tables = Table.objects.filter(
        orders__status__in=['pending', 'confirmed', 'preparing']
    ).distinct().count()
    print(f"🪑 Active Tables: {active_tables}")

    # Check total orders
    total_orders = Order.objects.count()
    print(f"📦 Total Orders: {total_orders}")

    # Check available tables
    total_tables = Table.objects.filter(is_active=True).count()
    print(f"🪑 Available Tables: {total_tables}")

    print("\n🏪 Vendor Status:")
    for vendor in Vendor.objects.all():
        print(f"   {vendor.name}: Ready for orders")

    # Check if clean state is achieved
    is_clean = (
        orders_today == 0 and
        unpaid_orders == 0 and
        active_tables == 0 and
        total_orders == 0
    )

    if is_clean:
        print("\n🎯 ✅ Clean state achieved successfully!")
        print("   📊 Orders Today: 0")
        print("   💰 Unpaid Orders: 0")
        print("   🪑 Active Tables: 0")
    else:
        print("\n❌ Clean state not achieved.")

    return is_clean

def main():
    """Main reset function"""
    print("🚀 Starting River Side Food Court Data Reset")
    print("="*50)

    try:
        # Step 1: Clear all existing data
        clear_all_data()

        # Step 2: Ensure clean state
        ensure_clean_state()

        # Step 3: Verify clean state
        success = verify_clean_state()

        if success:
            print("\n🎉 Data reset completed successfully!")
            print("Your dashboard should now show:")
            print("   📊 Orders Today: 0")
            print("   💰 Unpaid Orders: 0")
            print("   🪑 Active Tables: 0")
            print("\nSystem is ready for fresh orders!")
        else:
            print("\n⚠️  Data reset completed with warnings.")

    except Exception as e:
        print(f"\n❌ Error during reset: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
