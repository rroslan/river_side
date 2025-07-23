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

        logger.info(f"VendorConsumer: Connection attempt for vendor {self.vendor_id}")
        logger.info(f"VendorConsumer: User in scope: {self.scope.get('user')}")

        # Check if user has permission to access this vendor
        has_permission = await self.check_vendor_permission()
        logger.info(f"VendorConsumer: Permission check result: {has_permission}")

        if not has_permission:
            logger.warning(f"VendorConsumer: Permission denied for vendor {self.vendor_id}")
            await self.close()
            return

        # Join vendor group
        await self.channel_layer.group_add(
            self.vendor_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"VendorConsumer: Connection accepted for vendor {self.vendor_id}")

        # Send current orders for this vendor
        orders = await self.get_vendor_orders()
        logger.info(f"VendorConsumer: Sending {len(orders)} orders to vendor {self.vendor_id}")

        await self.send(text_data=json.dumps({
            'type': 'order_list',
            'orders': orders
        }))

        logger.info(f"Vendor {self.vendor_id} connected successfully")

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

            logger.info(f"VendorConsumer: Received message type: {message_type}")

            if message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))

            elif message_type == 'update_order_status':
                await self.update_order_status(data)

            elif message_type == 'get_orders':
                orders = await self.get_vendor_orders()
                await self.send(text_data=json.dumps({
                    'type': 'order_list',
                    'orders': orders
                }))

        except Exception as e:
            logger.error(f"Error in VendorConsumer.receive: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred'
            }))

    async def update_order_status(self, data):
        """Update order status"""
        order_id = data.get('order_id')
        new_status = data.get('status')

        if not order_id or not new_status:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Missing order_id or status'
            }))
            return

        success = await self.set_order_status(order_id, new_status)
        if success:
            # Send confirmation back to vendor
            await self.send(text_data=json.dumps({
                'type': 'order_status_change',
                'order_id': order_id,
                'status': new_status,
                'message': f'Order status updated to {new_status}'
            }))

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

                # Also notify other vendors if needed
                await self.channel_layer.group_send(
                    self.vendor_group_name,
                    {
                        'type': 'order_update',
                        'order': await self.get_full_order_data(order_id)
                    }
                )

                # Notify cashier dashboard about status change
                if new_status in ['ready', 'delivered']:
                    # Get updated statistics
                    cashier_consumer = CashierConsumer()
                    cashier_consumer.scope = {'user': self.scope['user']}
                    stats = await cashier_consumer.get_cashier_stats()

                    await self.channel_layer.group_send(
                        'cashier_dashboard',
                        {
                            'type': 'order_status_update',
                            'order_id': order_id,
                            'status': new_status,
                            'stats': stats,
                            'order': await self.get_order_for_cashier(order_id)
                        }
                    )
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to update order status'
            }))


    async def order_update(self, event):
        """Handle order update broadcast"""
        # Don't send to self if we initiated the update
        if event.get('sender_channel_name') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'order_update',
                'order': event['order']
            }))

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

        # Log authentication details
        logger.info(f"VendorConsumer.check_vendor_permission: User: {user}")
        logger.info(f"VendorConsumer.check_vendor_permission: Is authenticated: {user.is_authenticated if user else False}")

        if not user or not user.is_authenticated:
            logger.warning("VendorConsumer.check_vendor_permission: User not authenticated")
            return False

        try:
            vendor = Vendor.objects.get(id=self.vendor_id)
            is_owner = vendor.owner == user
            is_staff = user.is_staff

            logger.info(f"VendorConsumer.check_vendor_permission: Vendor owner: {vendor.owner}, Is owner: {is_owner}, Is staff: {is_staff}")

            return is_owner or is_staff
        except Vendor.DoesNotExist:
            logger.error(f"VendorConsumer.check_vendor_permission: Vendor {self.vendor_id} does not exist")
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
                        'order': {
                            'id': order_id,
                            'table_number': item.order.table.number,
                            'status': item.order.status,
                            'total_amount': str(item.order.total_amount),
                            'created_at': item.order.created_at.isoformat(),
                            'customer_name': item.order.customer_name,
                            'notes': item.order.notes
                        },
                        'items': []
                    }

                orders_data[order_id]['items'].append({
                    'id': item.id,
                    'name': item.menu_item.name,
                    'quantity': item.quantity,
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

            # Notify cashiers when order is ready for payment
            if new_status in ['ready', 'delivered']:
                from channels.layers import get_channel_layer
                channel_layer = get_channel_layer()

                # Get order details for cashier
                order_data = self.get_order_for_cashier_sync(order_id)

                if order_data:
                    import asyncio
                    async def notify_cashiers():
                        await channel_layer.group_send(
                            'cashier_dashboard',
                            {
                                'type': 'order_ready_for_payment',
                                'order': order_data
                            }
                        )
                    asyncio.create_task(notify_cashiers())

            return True
        except Order.DoesNotExist:
            return False

    def get_order_for_cashier_sync(self, order_id):
        """Synchronous version of get_order_for_cashier"""
        try:
            order = Order.objects.select_related('table').prefetch_related('items__menu_item__category__vendor').get(id=order_id)

            # Group items by vendor
            vendor_items = {}
            for item in order.items.all():
                vendor_name = item.menu_item.category.vendor.name
                if vendor_name not in vendor_items:
                    vendor_items[vendor_name] = []

                vendor_items[vendor_name].append({
                    'name': item.menu_item.name,
                    'quantity': item.quantity,
                    'price': str(item.unit_price),
                    'subtotal': str(item.subtotal)
                })

            return {
                'id': str(order.id),
                'table_number': order.table.number,
                'status': order.status,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.isoformat(),
                'customer_name': order.customer_name or 'Guest',
                'vendor_items': vendor_items,
                'time_elapsed': self.get_time_elapsed(order.created_at)
            }
        except Order.DoesNotExist:
            return None

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

    @database_sync_to_async
    def get_order_for_cashier(self, order_id):
        """Get order details formatted for cashier dashboard"""
        try:
            order = Order.objects.select_related('table').prefetch_related('items__menu_item__category__vendor').get(id=order_id)

            # Group items by vendor
            vendor_items = {}
            for item in order.items.all():
                vendor_name = item.menu_item.category.vendor.name
                if vendor_name not in vendor_items:
                    vendor_items[vendor_name] = []

                vendor_items[vendor_name].append({
                    'name': item.menu_item.name,
                    'quantity': item.quantity,
                    'price': str(item.unit_price),
                    'subtotal': str(item.subtotal)
                })

            return {
                'id': str(order.id),
                'table_number': order.table.number,
                'status': order.status,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.isoformat(),
                'customer_name': order.customer_name or 'Guest',
                'vendor_items': vendor_items,
                'time_elapsed': self.get_time_elapsed(order.created_at)
            }
        except Order.DoesNotExist:
            return None

    def get_time_elapsed(self, created_at):
        """Get human-readable time elapsed"""
        from django.utils import timezone
        now = timezone.now()
        diff = now - created_at

        minutes = int(diff.total_seconds() / 60)
        if minutes < 60:
            return f"{minutes} min ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days = hours // 24
        return f"{days}d ago"



class CashierConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for cashier dashboard - real-time payment updates"""

    async def connect(self):
        self.cashier_group_name = 'cashier_dashboard'

        # Check if user has cashier permissions
        if not await self.check_cashier_permission():
            await self.close()
            return

        # Join cashier group
        await self.channel_layer.group_add(
            self.cashier_group_name,
            self.channel_name
        )

        await self.accept()

        # Send current unpaid orders
        orders = await self.get_unpaid_orders()
        stats = await self.get_cashier_stats()
        await self.send(text_data=json.dumps({
            'type': 'order_list',
            'orders': orders,
            'stats': stats
        }))

        logger.info(f"Cashier {self.scope['user'].username} connected to dashboard")

    async def disconnect(self, close_code):
        # Leave cashier group
        await self.channel_layer.group_discard(
            self.cashier_group_name,
            self.channel_name
        )
        logger.info(f"Cashier disconnected")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))

            elif message_type == 'get_orders':
                orders = await self.get_unpaid_orders()
                stats = await self.get_cashier_stats()
                await self.send(text_data=json.dumps({
                    'type': 'order_list',
                    'orders': orders,
                    'stats': stats
                }))

            elif message_type == 'mark_paid':
                await self.mark_order_paid(data)

        except Exception as e:
            logger.error(f"Error in CashierConsumer.receive: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred'
            }))

    async def order_ready_for_payment(self, event):
        """Handle new order ready for payment"""
        await self.send(text_data=json.dumps({
            'type': 'new_order_ready',
            'order': event['order']
        }))

    async def order_payment_update(self, event):
        """Handle order payment update broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'order_payment_update',
            'order_id': event['order_id'],
            'status': event['status']
        }))

    async def order_status_update(self, event):
        """Handle order status update from vendors"""
        await self.send(text_data=json.dumps({
            'type': 'order_status_update',
            'order_id': event['order_id'],
            'status': event['status'],
            'stats': event.get('stats', {}),
            'order': event.get('order')
        }))

    @database_sync_to_async
    def check_cashier_permission(self):
        """Check if user has cashier permissions"""
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            return False

        # Check if user is in cashier group or has specific permissions
        return (user.groups.filter(name='Cashiers').exists() or
                user.has_perm('orders.change_order') or
                user.is_staff)

    @database_sync_to_async
    def get_unpaid_orders(self):
        """Get all unpaid orders ready for payment"""
        from django.utils import timezone

        orders = Order.objects.filter(
            status__in=['delivered', 'ready']
        ).select_related('table').prefetch_related('items__menu_item__category__vendor').order_by('-created_at')

        orders_data = []
        for order in orders:
            # Group items by vendor
            vendor_items = {}
            for item in order.items.all():
                vendor_name = item.menu_item.category.vendor.name
                if vendor_name not in vendor_items:
                    vendor_items[vendor_name] = []

                vendor_items[vendor_name].append({
                    'name': item.menu_item.name,
                    'quantity': item.quantity,
                    'price': str(item.unit_price),
                    'subtotal': str(item.subtotal)
                })

            orders_data.append({
                'id': str(order.id),
                'table_number': order.table.number,
                'status': order.status,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.isoformat(),
                'customer_name': order.customer_name or 'Guest',
                'vendor_items': vendor_items,
                'time_elapsed': self.get_time_elapsed(order.created_at)
            })

        return orders_data

    @database_sync_to_async
    def get_cashier_stats(self):
        """Get current statistics for cashier dashboard"""
        from django.utils import timezone
        from django.db.models import Sum
        from vendors.models import Table

        today = timezone.now().date()

        stats = {
            'total_orders_today': Order.objects.filter(created_at__date=today).count(),
            'unpaid_orders': Order.objects.filter(status__in=['delivered', 'ready']).count(),
            'paid_orders_today': Order.objects.filter(status='paid', created_at__date=today).count(),
            'total_revenue_today': float(Order.objects.filter(
                status='paid',
                created_at__date=today
            ).aggregate(total=Sum('total_amount'))['total'] or 0),
            'active_tables': Table.objects.filter(
                orders__status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
            ).distinct().count()
        }

        return stats

    @database_sync_to_async
    def mark_order_paid(self, data):
        """Mark an order as paid"""
        order_id = data.get('order_id')
        payment_method = data.get('payment_method', 'cash')
        payment_amount = data.get('payment_amount')

        try:
            order = Order.objects.get(id=order_id)
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.payment_method = payment_method
            if payment_amount:
                order.payment_amount = payment_amount
            order.save()

            # Notify all cashiers about the payment
            order_data = {
                'id': str(order.id),
                'table_number': order.table.number,
                'status': 'paid'
            }

            # Send update to all cashiers
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()

            async def send_update():
                await channel_layer.group_send(
                    self.cashier_group_name,
                    {
                        'type': 'order_payment_update',
                        'order_id': str(order.id),
                        'status': 'paid'
                    }
                )

            import asyncio
            asyncio.create_task(send_update())

            return True
        except Order.DoesNotExist:
            return False

    def get_time_elapsed(self, created_at):
        """Get human-readable time elapsed"""
        from django.utils import timezone
        now = timezone.now()
        diff = now - created_at

        minutes = int(diff.total_seconds() / 60)
        if minutes < 60:
            return f"{minutes} min ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days = hours // 24
        return f"{days}d ago"
