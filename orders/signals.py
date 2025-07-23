from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Order, OrderItem, OrderStatusHistory
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()

@receiver(post_save, sender=Order)
def order_created_or_updated(sender, instance, created, **kwargs):
    """Send real-time notification when order is created or updated"""
    try:
        if created:
            # New order created - notify all relevant parties
            send_new_order_notification(instance)
        else:
            # Order updated - notify table and vendors
            send_order_update_notification(instance)
    except Exception as e:
        logger.error(f"Error in order_created_or_updated signal: {e}")

@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """Track order status changes and update timestamps"""
    if instance.pk:  # Only for existing orders
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status != instance.status:
                # Status changed, update appropriate timestamp
                now = timezone.now()

                if instance.status == 'confirmed' and not instance.confirmed_at:
                    instance.confirmed_at = now
                    # Calculate estimated ready time
                    prep_time = instance.get_preparation_time()
                    instance.estimated_ready_time = now + timezone.timedelta(minutes=prep_time)

                elif instance.status == 'ready' and not instance.ready_at:
                    instance.ready_at = now

                elif instance.status == 'delivered' and not instance.delivered_at:
                    instance.delivered_at = now

                elif instance.status == 'paid' and not instance.paid_at:
                    instance.paid_at = now

                # Create status history entry
                OrderStatusHistory.objects.create(
                    order=instance,
                    status=instance.status,
                    notes=f"Status changed from {old_order.status} to {instance.status}"
                )

        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=OrderItem)
def order_item_updated(sender, instance, created, **kwargs):
    """Send notification when order item is updated"""
    try:
        if not created:  # Only for updates, not creation
            send_order_item_update_notification(instance)
    except Exception as e:
        logger.error(f"Error in order_item_updated signal: {e}")

def send_new_order_notification(order):
    """Send new order notification to all relevant channels"""
    order_data = serialize_order_for_notification(order)

    # Notify customer table
    table_group = f'table_{order.table.number}'
    async_to_sync(channel_layer.group_send)(table_group, {
        'type': 'new_order',
        'order': order_data
    })

    # Notify each vendor involved in the order
    try:
        from vendors.models import Vendor
        vendor_ids = set()
        for item in order.items.all():
            vendor_ids.add(item.menu_item.category.vendor.id)

        for vendor_id in vendor_ids:
            vendor_group = f'vendor_{vendor_id}'
            async_to_sync(channel_layer.group_send)(vendor_group, {
                'type': 'new_order_for_vendor',
                'order': order_data
            })
    except Exception as e:
        logger.error(f"Error notifying vendors: {e}")



    logger.info(f"New order notification sent for order {order.id}")

def send_order_update_notification(order):
    """Send order update notification"""
    order_data = serialize_order_for_notification(order)

    # Notify customer table
    table_group = f'table_{order.table.number}'
    async_to_sync(channel_layer.group_send)(table_group, {
        'type': 'order_update',
        'order': order_data
    })

    # Notify vendors involved in this order
    try:
        from vendors.models import Vendor
        vendor_ids = set()
        for item in order.items.all():
            vendor_ids.add(item.menu_item.category.vendor.id)

        for vendor_id in vendor_ids:
            vendor_group = f'vendor_{vendor_id}'
            async_to_sync(channel_layer.group_send)(vendor_group, {
                'type': 'order_update',
                'order': order_data
            })
    except Exception as e:
        logger.error(f"Error notifying vendors: {e}")



    logger.info(f"Order update notification sent for order {order.id}")

def send_order_item_update_notification(order_item):
    """Send notification when individual order item is updated"""
    order = order_item.order
    order_data = serialize_order_for_notification(order)

    # Notify customer table
    table_group = f'table_{order.table.number}'
    async_to_sync(channel_layer.group_send)(table_group, {
        'type': 'order_update',
        'order': order_data
    })

    # Notify vendor
    vendor_group = f'vendor_{order_item.vendor.id}'
    async_to_sync(channel_layer.group_send)(vendor_group, {
        'type': 'order_update',
        'order': order_data
    })

def serialize_order_for_notification(order):
    """Serialize order data for WebSocket notifications"""
    items = []
    for item in order.items.all():
        items.append({
            'id': item.id,
            'name': item.menu_item.name,
            'quantity': item.quantity,
            'unit_price': str(item.unit_price),
            'subtotal': str(item.subtotal),
            'vendor': item.vendor.name,
            'vendor_id': item.vendor.id,

            'special_instructions': item.special_instructions,
            'preparation_time': item.menu_item.preparation_time
        })

    return {
        'id': str(order.id),
        'table_number': order.table.number,
        'status': order.status,
        'total_amount': str(order.total_amount),
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
        'confirmed_at': order.confirmed_at.isoformat() if order.confirmed_at else None,
        'ready_at': order.ready_at.isoformat() if order.ready_at else None,
        'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
        'paid_at': order.paid_at.isoformat() if order.paid_at else None,
        'estimated_ready_time': order.estimated_ready_time.isoformat() if order.estimated_ready_time else None,
        'customer_name': order.customer_name,
        'notes': order.notes,
        'items': items
    }

def send_order_status_change_notification(order, old_status, new_status, message=""):
    """Send specific status change notification"""
    # Notify customer table
    table_group = f'table_{order.table.number}'
    async_to_sync(channel_layer.group_send)(table_group, {
        'type': 'order_status_change',
        'order_id': str(order.id),
        'old_status': old_status,
        'new_status': new_status,
        'status': new_status,
        'message': message or f'Your order status has been updated to {new_status.title()}'
    })

    logger.info(f"Status change notification sent: {old_status} -> {new_status} for order {order.id}")
