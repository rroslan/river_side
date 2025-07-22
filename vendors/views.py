from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Vendor, MenuItem, Category
from orders.models import Order, OrderItem, OrderStatus
import json

@login_required
def vendor_dashboard(request, vendor_id):
    """Vendor dashboard with real-time orders"""
    vendor = get_object_or_404(Vendor, id=vendor_id)

    # Check if user has permission
    if vendor.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this vendor dashboard')
        return redirect('vendor_list')

    # Get current orders for this vendor
    current_orders = OrderItem.objects.filter(
        menu_item__category__vendor=vendor,
        order__status__in=['pending', 'confirmed', 'preparing', 'ready']
    ).select_related('order', 'menu_item').order_by('-order__created_at')

    # Group orders by order ID and serialize data
    orders_dict = {}
    for item in current_orders:
        order_id = item.order.id
        if order_id not in orders_dict:
            orders_dict[order_id] = {
                'order': {
                    'id': str(item.order.id),
                    'table_number': item.order.table.number,
                    'status': item.order.status,
                    'total_amount': str(item.order.total_amount),
                    'customer_name': item.order.customer_name,
                    'created_at': item.order.created_at.isoformat(),
                    'notes': item.order.notes
                },
                'items': []
            }

        orders_dict[order_id]['items'].append({
            'id': item.id,
            'name': item.menu_item.name,
            'quantity': item.quantity,
            'special_instructions': item.special_instructions,
            'preparation_time': item.menu_item.preparation_time
        })

    orders = list(orders_dict.values())

    # Get statistics
    today = timezone.now().date()
    stats = {
        'pending_orders': len([o for o in orders if o['order'].status == 'pending']),
        'preparing_orders': len([o for o in orders if o['order'].status == 'preparing']),
        'ready_orders': len([o for o in orders if o['order'].status == 'ready']),
        'todays_orders': OrderItem.objects.filter(
            menu_item__category__vendor=vendor,
            order__created_at__date=today
        ).count()
    }

    context = {
        'vendor': vendor,
        'orders': orders,
        'stats': stats
    }

    return render(request, 'vendors/dashboard.html', context)

@login_required
def vendor_list(request):
    """List all vendors for the user"""
    if request.user.is_staff:
        vendors = Vendor.objects.all()
    else:
        vendors = Vendor.objects.filter(owner=request.user)

    return render(request, 'vendors/vendor_list.html', {'vendors': vendors})

@login_required
@require_http_methods(["POST"])
def update_order_status(request, vendor_id):
    """Update order status via AJAX"""
    try:
        vendor = get_object_or_404(Vendor, id=vendor_id)

        # Check permission
        if vendor.owner != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('status')

        if not order_id or not new_status:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        if new_status not in [choice[0] for choice in OrderStatus.choices]:
            return JsonResponse({'error': 'Invalid status'}, status=400)

        order = get_object_or_404(Order, id=order_id)

        # Verify this vendor has items in this order
        vendor_items = OrderItem.objects.filter(
            order=order,
            menu_item__category__vendor=vendor
        )

        if not vendor_items.exists():
            return JsonResponse({'error': 'This order does not contain items from your vendor'}, status=403)

        # Update order status
        old_status = order.status
        order.status = new_status
        order.save()

        return JsonResponse({
            'success': True,
            'message': f'Order status updated from {old_status} to {new_status}',
            'order_id': str(order.id),
            'new_status': new_status
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def menu_management(request, vendor_id):
    """Manage vendor menu items"""
    vendor = get_object_or_404(Vendor, id=vendor_id)

    # Check permission
    if vendor.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to manage this vendor')
        return redirect('vendor_list')

    categories = Category.objects.filter(vendor=vendor).prefetch_related('menu_items')

    context = {
        'vendor': vendor,
        'categories': categories
    }

    return render(request, 'vendors/menu_management.html', context)

@login_required
@require_http_methods(["POST"])
def toggle_menu_item(request, vendor_id):
    """Toggle menu item availability"""
    try:
        vendor = get_object_or_404(Vendor, id=vendor_id)

        # Check permission
        if vendor.owner != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        data = json.loads(request.body)
        item_id = data.get('item_id')

        menu_item = get_object_or_404(MenuItem, id=item_id, category__vendor=vendor)
        menu_item.is_available = not menu_item.is_available
        menu_item.save()

        return JsonResponse({
            'success': True,
            'item_id': item_id,
            'is_available': menu_item.is_available,
            'message': f'{menu_item.name} is now {"available" if menu_item.is_available else "unavailable"}'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def kitchen_display(request):
    """Kitchen display system showing all orders"""
    # Get all active orders
    orders = Order.objects.filter(
        status__in=['pending', 'confirmed', 'preparing']
    ).order_by('created_at')

    # Group by vendor for better organization
    orders_by_vendor = {}
    for order in orders:
        for item in order.items.all():
            vendor_name = item.vendor.name
            if vendor_name not in orders_by_vendor:
                orders_by_vendor[vendor_name] = []

            # Check if order already added for this vendor
            order_exists = any(o['order'].id == order.id for o in orders_by_vendor[vendor_name])
            if not order_exists:
                vendor_items = [i for i in order.items.all() if i.vendor.name == vendor_name]
                orders_by_vendor[vendor_name].append({
                    'order': order,
                    'items': vendor_items
                })

    context = {
        'orders_by_vendor': orders_by_vendor,
        'total_orders': orders.count()
    }

    return render(request, 'vendors/kitchen_display.html', context)
