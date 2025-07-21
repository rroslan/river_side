import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Order, OrderItem, OrderStatus
from vendors.models import Vendor, Table

logger = logging.getLogger(__name__)

class OrderConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time order updates"""

    async def connect(self):
        self.table_number = self.scope['url_route']['kwargs']['table_number']
        self.table_group_name = f'table_{self.table_number}'

        # Join table group
        await self.channel_layer.group_add(
            self.table_group_name,
            self.channel_name
        )

        await self.accept()

        # Send current orders for this table
        orders = await self.get_table_orders()
        await self.send(text_data=json.dumps({
            'type': 'order_list',
            'orders': orders
        }))

        logger.info(f"Customer connected to table {self.table_number}")

    async def disconnect(self, close_code):
        # Leave table group
        await self.channel_layer.group_discard(
            self.table_group_name,
            self.channel_name
        )
        logger.info(f"Customer disconnected from table {self.table_number}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))

            elif message_type == 'get_orders':
                orders = await self.get_table_orders()
                await self.send(text_data=json.dumps({
                    'type': 'order_list',
                    'orders': orders
                }))

        except Exception as e:
            logger.error(f"Error in OrderConsumer.receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred'
            }))

    async def order_update(self, event):
        """Handle order update from group"""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'order': event['order']
        }))

    async def order_status_change(self, event):
        """Handle order status change from group"""
        await self.send(text_data=json.dumps({
            'type': 'order_status_change',
            'order_id': event['order_id'],
            'status': event['status'],
            'message': event.get('message', '')
        }))

    async def new_order(self, event):
        """Handle new order notification"""
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order': event['order']
        }))

    @database_sync_to_async
    def get_table_orders(self):
        """Get current orders for the table"""
        try:
            table = Table.objects.get(number=self.table_number)
            orders = Order.objects.filter(
                table=table,
                status__in=['pending', 'confirmed', 'preparing', 'ready']
            ).order_by('-created_at')

            orders_data = []
            for order in orders:
                order_items = []
                for item in order.items.all():
                    order_items.append({
                        'id': item.id,
                        'name': item.menu_item.name,
                        'quantity': item.quantity,
                        'unit_price': str(item.unit_price),
                        'subtotal': str(item.subtotal),
                        'vendor': item.vendor.name,
                        'status': item.status,
                        'special_instructions': item.special_instructions
                    })

                orders_data.append({
                    'id': str(order.id),
                    'status': order.status,
                    'total_amount': str(order.total_amount),
                    'created_at': order.created_at.isoformat(),
                    'estimated_ready_time': order.estimated_ready_time.isoformat() if order.estimated_ready_time else None,
                    'items': order_items,
                    'customer_name': order.customer_name,
                    'notes': order.notes
                })

            return orders_data
        except Table.DoesNotExist:
            return []


class VendorConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for vendor dashboard"""

    async def connect(self):
        self.vendor_id = self.scope['url_route']['kwargs']['vendor_id']
        self.vendor_group_name = f'vendor_{self.vendor_id}'

        # Check if user has permission to access this vendor
        if not await self.check_vendor_permission():
            await self.close()
            return

        # Join vendor group
        await self.channel_layer.group_add(
            self.vendor_group_name,
            self.channel_name
        )

        await self.accept()

        # Send current orders for this vendor
        orders = await self.get_vendor_orders()
        await self.send(text_data=json.dumps({
            'type': 'order_list',
            'orders': orders
        }))

        logger.info(f"Vendor {self.vendor_id} connected")

    async def disconnect(self, close_code):
        # Leave vendor group
        await self.channel_layer.group_discard(
            self.vendor_group_name,
            self.channel_name
        )
        logger.info(f"Vendor {self.vendor_id} disconnected")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'update_order_status':
                await self.update_order_status(data)

            elif message_type == 'update_item_status':
                await self.update_item_status(data)

            elif message_type == 'get_orders':
                orders = await self.get_vendor_orders()
                await self.send(text_data=json.dumps({
                    'type': 'order_list',
                    'orders': orders
                }))

        except Exception as e:
            logger.error(f"Error in VendorConsumer.receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred'
            }))

    async def update_order_status(self, data):
        """Update order status"""
        order_id = data.get('order_id')
        new_status = data.get('status')

        if not order_id or not new_status:
            return

        success = await self.set_order_status(order_id, new_status)
        if success:
            # Notify the table about status change
            order = await self.get_order_details(order_id)
            if order:
                await self.channel_layer.group_send(
                    f'table_{order["table_number"]}',
                    {
                        'type': 'order_status_change',
                        'order_id': order_id,
                        'status': new_status,
                        'message': f'Order status updated to {new_status}'
                    }
                )

    async def update_item_status(self, data):
        """Update individual item status"""
        item_id = data.get('item_id')
        new_status = data.get('status')

        if not item_id or not new_status:
            return

        success = await self.set_item_status(item_id, new_status)
        if success:
            # Get order info and notify table
            order_info = await self.get_order_from_item(item_id)
            if order_info:
                await self.channel_layer.group_send(
                    f'table_{order_info["table_number"]}',
                    {
                        'type': 'order_update',
                        'order': order_info
                    }
                )

    async def new_order_for_vendor(self, event):
        """Handle new order notification for vendor"""
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order': event['order']
        }))

    @database_sync_to_async
    def check_vendor_permission(self):
        """Check if user has permission to access vendor dashboard"""
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            return False

        try:
            vendor = Vendor.objects.get(id=self.vendor_id)
            return vendor.owner == user or user.is_staff
        except Vendor.DoesNotExist:
            return False

    @database_sync_to_async
    def get_vendor_orders(self):
        """Get current orders for the vendor"""
        try:
            vendor = Vendor.objects.get(id=self.vendor_id)

            # Get orders that contain items from this vendor
            order_items = OrderItem.objects.filter(
                menu_item__category__vendor=vendor,
                order__status__in=['pending', 'confirmed', 'preparing', 'ready']
            ).select_related('order', 'menu_item').order_by('-order__created_at')

            orders_data = {}
            for item in order_items:
                order_id = str(item.order.id)
                if order_id not in orders_data:
                    orders_data[order_id] = {
                        'id': order_id,
                        'table_number': item.order.table.number,
                        'status': item.order.status,
                        'total_amount': str(item.order.total_amount),
                        'created_at': item.order.created_at.isoformat(),
                        'customer_name': item.order.customer_name,
                        'items': []
                    }

                orders_data[order_id]['items'].append({
                    'id': item.id,
                    'name': item.menu_item.name,
                    'quantity': item.quantity,
                    'status': item.status,
                    'special_instructions': item.special_instructions,
                    'preparation_time': item.menu_item.preparation_time
                })

            return list(orders_data.values())
        except Vendor.DoesNotExist:
            return []

    @database_sync_to_async
    def set_order_status(self, order_id, new_status):
        """Update order status"""
        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save()

            # Create status history
            from .models import OrderStatusHistory
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                changed_by=self.scope.get('user')
            )

            return True
        except Order.DoesNotExist:
            return False

    @database_sync_to_async
    def set_item_status(self, item_id, new_status):
        """Update order item status"""
        try:
            item = OrderItem.objects.get(id=item_id)
            item.status = new_status
            item.save()
            return True
        except OrderItem.DoesNotExist:
            return False

    @database_sync_to_async
    def get_order_details(self, order_id):
        """Get order details"""
        try:
            order = Order.objects.get(id=order_id)
            return {
                'id': str(order.id),
                'table_number': order.table.number,
                'status': order.status
            }
        except Order.DoesNotExist:
            return None

    @database_sync_to_async
    def get_order_from_item(self, item_id):
        """Get order info from item"""
        try:
            item = OrderItem.objects.select_related('order').get(id=item_id)
            order = item.order

            # Get all items for this order
            items = []
            for order_item in order.items.all():
                items.append({
                    'id': order_item.id,
                    'name': order_item.menu_item.name,
                    'quantity': order_item.quantity,
                    'status': order_item.status,
                    'vendor': order_item.vendor.name
                })

            return {
                'id': str(order.id),
                'table_number': order.table.number,
                'status': order.status,
                'items': items
            }
        except OrderItem.DoesNotExist:
            return None


class KitchenConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for kitchen display system"""

    async def connect(self):
        self.kitchen_group_name = 'kitchen_display'

        # Join kitchen group
        await self.channel_layer.group_add(
            self.kitchen_group_name,
            self.channel_name
        )

        await self.accept()

        # Send all active orders
        orders = await self.get_all_active_orders()
        await self.send(text_data=json.dumps({
            'type': 'order_list',
            'orders': orders
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.kitchen_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'get_orders':
                orders = await self.get_all_active_orders()
                await self.send(text_data=json.dumps({
                    'type': 'order_list',
                    'orders': orders
                }))

        except Exception as e:
            logger.error(f"Error in KitchenConsumer.receive: {e}")

    async def new_order_kitchen(self, event):
        """Handle new order for kitchen display"""
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order': event['order']
        }))

    async def order_update_kitchen(self, event):
        """Handle order update for kitchen display"""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'order': event['order']
        }))

    @database_sync_to_async
    def get_all_active_orders(self):
        """Get all active orders for kitchen display"""
        orders = Order.objects.filter(
            status__in=['pending', 'confirmed', 'preparing']
        ).order_by('created_at')

        orders_data = []
        for order in orders:
            items_by_vendor = {}
            for item in order.items.all():
                vendor_name = item.vendor.name
                if vendor_name not in items_by_vendor:
                    items_by_vendor[vendor_name] = []

                items_by_vendor[vendor_name].append({
                    'id': item.id,
                    'name': item.menu_item.name,
                    'quantity': item.quantity,
                    'status': item.status,
                    'special_instructions': item.special_instructions
                })

            orders_data.append({
                'id': str(order.id),
                'table_number': order.table.number,
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'items_by_vendor': items_by_vendor,
                'total_amount': str(order.total_amount)
            })

        return orders_data
