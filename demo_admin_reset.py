#!/usr/bin/env python
"""
Demonstration script for the Admin Demo Data Reset Feature
Shows how to use the new admin integration for triggering init_demo_data.py

This script demonstrates all the ways you can reset demo data:
1. Management command
2. Programmatic API calls
3. Admin interface simulation

Author: River Side Food Court Development Team
Version: 1.0
"""

import os
import sys
import django
import time
import requests
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from vendors.models import Vendor, Table
from orders.models import Order


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)


def print_stats():
    """Print current system statistics"""
    today = timezone.now().date()

    stats = {
        'orders_today': Order.objects.filter(created_at__date=today).count(),
        'unpaid_orders': Order.objects.filter(status__in=['delivered', 'ready']).count(),
        'active_tables': Table.objects.filter(
            orders__status__in=['pending', 'confirmed', 'preparing']
        ).distinct().count(),
        'total_orders': Order.objects.count(),
        'total_tables': Table.objects.filter(is_active=True).count(),
        'vendors': Vendor.objects.filter(is_active=True).count(),
    }

    print("\n📊 Current System Statistics:")
    print(f"   📦 Orders Today: {stats['orders_today']}")
    print(f"   💰 Unpaid Orders: {stats['unpaid_orders']}")
    print(f"   🪑 Active Tables: {stats['active_tables']}")
    print(f"   📋 Total Orders: {stats['total_orders']}")
    print(f"   🪑 Available Tables: {stats['total_tables']}")
    print(f"   🏪 Active Vendors: {stats['vendors']}")

    return stats


def demo_management_command():
    """Demonstrate the Django management command"""
    print_header("Django Management Command Demo")

    print("📝 The management command can be used in several ways:")
    print("\n1. Interactive mode (with confirmation):")
    print("   python manage.py reset_demo_data")

    print("\n2. Force mode (no confirmation - for scripts):")
    print("   python manage.py reset_demo_data --force")

    print("\n3. With verbosity control:")
    print("   python manage.py reset_demo_data --force --verbosity=2")

    print("\n🚀 Demonstrating force mode...")

    try:
        call_command('reset_demo_data', '--force', verbosity=1)
        print("✅ Management command completed successfully!")
    except Exception as e:
        print(f"❌ Management command failed: {e}")


def demo_admin_client():
    """Demonstrate admin interface using Django test client"""
    print_header("Admin Interface Demo (Programmatic)")

    # Create or get admin user
    admin_user, created = User.objects.get_or_create(
        username='demo_admin',
        defaults={
            'email': 'admin@riversidefoodcourt.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )

    if created:
        admin_user.set_password('demo123')
        admin_user.save()
        print("👤 Created demo admin user")
    else:
        print("👤 Using existing demo admin user")

    # Test admin interface
    client = Client()
    login_success = client.login(username='demo_admin', password='demo123')

    if not login_success:
        print("❌ Failed to login to admin interface")
        return

    print("✅ Successfully logged into admin interface")

    # Test admin URLs
    urls_to_test = [
        ('/admin/', 'Admin Index'),
        ('/admin/data-reset/', 'Data Reset Page'),
        ('/admin/api/stats/', 'Stats API'),
    ]

    for url, name in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {name}: Accessible")

                if url == '/admin/api/stats/':
                    data = response.json()
                    print(f"   📊 API Response: {data}")
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

    # Test data reset via POST
    print("\n🔄 Testing data reset via admin interface...")
    try:
        response = client.post('/admin/data-reset/',
                             data={},
                             HTTP_CONTENT_TYPE='application/json')

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Admin interface reset completed successfully!")
            else:
                print(f"❌ Admin interface reset failed: {result.get('message')}")
        else:
            print(f"❌ Admin interface reset failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin interface reset error: {e}")


def demo_admin_action():
    """Demonstrate the admin action functionality"""
    print_header("Admin Action Demo")

    print("📝 The admin action can be used from the Orders admin page:")
    print("   1. Go to /admin/orders/order/")
    print("   2. Select any orders (selection doesn't affect the action)")
    print("   3. Choose '🔄 Reset All Demo Data' from Actions dropdown")
    print("   4. Click 'Go' to execute")

    # We'll simulate this by importing and calling the action directly
    from orders.admin import reset_demo_data_action

    print("\n🎭 Simulating admin action call...")

    class MockModelAdmin:
        pass

    class MockRequest:
        def __init__(self):
            self.user = User.objects.filter(is_superuser=True).first()
            self._messages = []

    try:
        mock_admin = MockModelAdmin()
        mock_request = MockRequest()
        mock_queryset = Order.objects.none()  # Empty queryset

        reset_demo_data_action(mock_admin, mock_request, mock_queryset)
        print("✅ Admin action executed successfully!")

    except Exception as e:
        print(f"❌ Admin action failed: {e}")


def create_sample_data():
    """Create some sample data to demonstrate the reset"""
    print_header("Creating Sample Data")

    print("🏗️ Creating sample orders for demonstration...")

    from vendors.models import MenuItem
    from orders.models import Order, OrderItem

    # Get a menu item and table
    menu_item = MenuItem.objects.filter(is_available=True).first()
    table = Table.objects.filter(is_active=True).first()

    if not menu_item or not table:
        print("⚠️ No menu items or tables available. Skipping sample data creation.")
        return

    # Create a few sample orders
    for i in range(3):
        order = Order.objects.create(
            table=table,
            customer_name=f"Demo Customer {i+1}",
            customer_phone=f"555-000{i+1}",
            status='pending',
            notes=f"Demo order {i+1} for reset demonstration"
        )

        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=2,
            unit_price=menu_item.price,
            special_instructions="Demo order item"
        )

        order.calculate_total()
        print(f"   📦 Created demo order #{order.id}")

    print("✅ Sample data created successfully!")


def demo_workflow():
    """Demonstrate complete workflow"""
    print_header("Complete Workflow Demonstration")

    print("🎬 This demonstration will show the complete workflow:")
    print("   1. Show current system state")
    print("   2. Create sample data")
    print("   3. Show updated state")
    print("   4. Reset data using management command")
    print("   5. Verify clean state")

    input("\nPress Enter to continue...")

    # Step 1: Initial state
    print("\n1️⃣ Initial System State:")
    initial_stats = print_stats()

    # Step 2: Create sample data
    print("\n2️⃣ Creating Sample Data:")
    create_sample_data()

    # Step 3: Updated state
    print("\n3️⃣ Updated System State:")
    updated_stats = print_stats()

    # Step 4: Reset data
    print("\n4️⃣ Resetting Data:")
    demo_management_command()

    # Step 5: Final state
    print("\n5️⃣ Final System State:")
    final_stats = print_stats()

    # Summary
    print("\n📈 Summary of Changes:")
    print(f"   📦 Orders: {initial_stats['total_orders']} → {updated_stats['total_orders']} → {final_stats['total_orders']}")
    print(f"   🪑 Active Tables: {initial_stats['active_tables']} → {updated_stats['active_tables']} → {final_stats['active_tables']}")

    if final_stats['total_orders'] == 0 and final_stats['active_tables'] == 0:
        print("\n🎉 Reset demonstration completed successfully!")
        print("   The system is now in a clean state ready for demos.")
    else:
        print("\n⚠️ Reset may not have completed fully. Please check manually.")


def show_feature_summary():
    """Show summary of all available features"""
    print_header("Feature Summary")

    features = [
        {
            'name': 'Management Command',
            'usage': 'python manage.py reset_demo_data --force',
            'description': 'Command-line interface for scripting and automation'
        },
        {
            'name': 'Admin Interface',
            'usage': '/admin/data-reset/',
            'description': 'Web interface with real-time progress tracking'
        },
        {
            'name': 'Admin Dashboard',
            'usage': '/admin/ (see Demo Data Management section)',
            'description': 'Quick access from main admin page with live stats'
        },
        {
            'name': 'Admin Action',
            'usage': 'Orders admin → Actions → Reset All Demo Data',
            'description': 'Quick action available from any admin list view'
        },
        {
            'name': 'Stats API',
            'usage': 'GET /admin/api/stats/',
            'description': 'RESTful endpoint for real-time system statistics'
        }
    ]

    print("🎯 Available Methods to Reset Demo Data:\n")

    for i, feature in enumerate(features, 1):
        print(f"{i}. {feature['name']}")
        print(f"   Usage: {feature['usage']}")
        print(f"   Description: {feature['description']}\n")

    print("🔐 Security Features:")
    print("   • All methods require Django admin authentication")
    print("   • Multiple confirmation steps prevent accidental resets")
    print("   • Comprehensive error handling and logging")
    print("   • CSRF protection for web interfaces")

    print("\n📋 What Gets Reset:")
    print("   ✅ All orders and order items")
    print("   ✅ Order status history")
    print("   ✅ Shopping cart data")
    print("   ❌ Vendors, categories, menu items (preserved)")
    print("   ❌ User accounts and authentication (preserved)")
    print("   ❌ System settings and configuration (preserved)")


def main():
    """Main demonstration function"""
    print("🚀 River Side Food Court - Admin Demo Reset Feature")
    print("="*60)
    print("This script demonstrates the new admin integration for demo data reset.")
    print("You can now trigger the init_demo_data.py functionality from the Django admin!")

    while True:
        print("\n🎯 Choose a demonstration:")
        print("1. Complete Workflow Demo")
        print("2. Management Command Demo")
        print("3. Admin Interface Demo")
        print("4. Admin Action Demo")
        print("5. Feature Summary")
        print("6. Current System Stats")
        print("0. Exit")

        choice = input("\nEnter your choice (0-6): ").strip()

        if choice == '0':
            print("\n👋 Thanks for exploring the Admin Demo Reset feature!")
            print("🔗 For more information, see: ADMIN_DEMO_RESET.md")
            break
        elif choice == '1':
            demo_workflow()
        elif choice == '2':
            demo_management_command()
        elif choice == '3':
            demo_admin_client()
        elif choice == '4':
            demo_admin_action()
        elif choice == '5':
            show_feature_summary()
        elif choice == '6':
            print_stats()
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demonstration interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demonstration error: {e}")
        import traceback
        traceback.print_exc()
