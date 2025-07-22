#!/usr/bin/env python
"""
Simple WebSocket Test for River Side Food Court

This script tests WebSocket connectivity using a simplified approach
to verify that real-time features are working properly.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add Django settings
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import Django channels testing tools
from channels.testing import WebsocketCommunicator
from orders.consumers import OrderConsumer, VendorConsumer, KitchenConsumer

async def test_order_consumer():
    """Test the OrderConsumer WebSocket"""
    print("🔗 Testing OrderConsumer (Table Orders)...")

    try:
        communicator = WebsocketCommunicator(OrderConsumer.as_asgi(), "/ws/orders/table/1/")
        connected, subprotocol = await communicator.connect()

        if connected:
            print("   ✅ Connected successfully")

            # Send a ping message
            await communicator.send_json_to({"type": "ping"})
            print("   📤 Sent ping message")

            # Try to receive a response
            try:
                response = await asyncio.wait_for(communicator.receive_json_from(), timeout=2)
                print(f"   📥 Received: {response}")
            except asyncio.TimeoutError:
                print("   ℹ️  No immediate response (normal for order consumer)")

            await communicator.disconnect()
            print("   ✅ Disconnected cleanly")
            return True
        else:
            print("   ❌ Failed to connect")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_vendor_consumer():
    """Test the VendorConsumer WebSocket"""
    print("\n🔗 Testing VendorConsumer (Vendor Orders)...")

    try:
        communicator = WebsocketCommunicator(VendorConsumer.as_asgi(), "/ws/orders/vendor/1/")
        connected, subprotocol = await communicator.connect()

        if connected:
            print("   ✅ Connected successfully")
            await communicator.disconnect()
            print("   ✅ Disconnected cleanly")
            return True
        else:
            print("   ❌ Failed to connect")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_kitchen_consumer():
    """Test the KitchenConsumer WebSocket"""
    print("\n🔗 Testing KitchenConsumer (Kitchen Display)...")

    try:
        communicator = WebsocketCommunicator(KitchenConsumer.as_asgi(), "/ws/orders/kitchen/")
        connected, subprotocol = await communicator.connect()

        if connected:
            print("   ✅ Connected successfully")
            await communicator.disconnect()
            print("   ✅ Disconnected cleanly")
            return True
        else:
            print("   ❌ Failed to connect")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_channel_layers():
    """Test the channel layer configuration"""
    print("\n🔗 Testing Channel Layer Configuration...")

    try:
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()

        if channel_layer is None:
            print("   ❌ No channel layer configured")
            return False

        # Test sending a message to ourselves
        test_group = "test_group"
        test_channel = await channel_layer.new_channel()

        await channel_layer.group_add(test_group, test_channel)
        await channel_layer.group_send(test_group, {
            "type": "test.message",
            "text": "Hello from test!"
        })

        # Try to receive the message
        message = await channel_layer.receive(test_channel)

        if message and message.get("text") == "Hello from test!":
            print("   ✅ Channel layer working correctly")
            print(f"   ℹ️  Using: {type(channel_layer).__name__}")
            return True
        else:
            print("   ❌ Channel layer not working properly")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def check_database():
    """Check if database has test data"""
    print("\n🔗 Checking Database for Test Data...")

    try:
        from vendors.models import Table, Vendor
        from orders.models import Order

        table_count = Table.objects.count()
        vendor_count = Vendor.objects.count()
        order_count = Order.objects.count()

        print(f"   📊 Tables: {table_count}")
        print(f"   📊 Vendors: {vendor_count}")
        print(f"   📊 Orders: {order_count}")

        if table_count > 0 and vendor_count > 0:
            print("   ✅ Database has test data")
            return True
        else:
            print("   ⚠️  Database missing test data")
            print("   💡 Run: python manage.py create_sample_data")
            return False

    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 River Side Food Court - WebSocket System Test")
    print("=" * 60)

    tests = [
        ("Database Check", check_database()),
        ("Channel Layer", test_channel_layers()),
        ("Order Consumer", test_order_consumer()),
        ("Vendor Consumer", test_vendor_consumer()),
        ("Kitchen Consumer", test_kitchen_consumer()),
    ]

    results = []
    for test_name, test_coro in tests:
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} failed with error: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")

    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if not success:
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed! WebSocket system is ready.")
        print("💡 You can now run: python run_server.py")
    else:
        print("\n⚠️  Some tests failed.")
        print("💡 Check the error messages above for details.")
        print("💡 Make sure to run: python manage.py create_sample_data")

    return all_passed

if __name__ == '__main__':
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
