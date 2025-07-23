from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Vendor, MenuItem, Category
from orders.models import Order, OrderItem, OrderStatus
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def vendor_redirect(request):
    """Redirect vendors directly to their own vendor dashboard after login"""
    # Get the vendor owned by this user
    try:
        vendor = Vendor.objects.get(owner=request.user)
        return redirect('vendors:vendor_dashboard', vendor_id=vendor.id)
    except Vendor.DoesNotExist:
        messages.error(request, 'No vendor account found for this user.')
        return redirect('login')
    except Vendor.MultipleObjectsReturned:
        # If multiple vendors, go to vendor list to choose
        return redirect('vendors:vendor_list')

def vendor_logout(request):
    """Custom logout view for vendors"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def vendor_dashboard(request, vendor_id):
    """Vendor dashboard with real-time orders"""
    vendor = get_object_or_404(Vendor, id=vendor_id)

    # Log which template will be used
    import logging
    logger = logging.getLogger(__name__)



    # Check if user has permission
    if vendor.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this vendor dashboard')
        return redirect('login')

    # Get current orders for this vendor (including delivered orders for payment tracking)
    current_orders = OrderItem.objects.filter(
        menu_item__category__vendor=vendor,
        order__status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
    ).select_related('order', 'menu_item').order_by('-order__created_at')

    # Get paid orders for revenue tracking
    paid_orders = OrderItem.objects.filter(
        menu_item__category__vendor=vendor,
        order__status='paid'
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

    # Process paid orders for revenue tracking
    paid_orders_dict = {}
    for item in paid_orders:
        order_id = item.order.id
        if order_id not in paid_orders_dict:
            paid_orders_dict[order_id] = {
                'order': {
                    'id': str(item.order.id),
                    'table_number': item.order.table.number,
                    'status': item.order.status,
                    'total_amount': str(item.order.total_amount),
                    'customer_name': item.order.customer_name,
                    'created_at': item.order.created_at.isoformat(),
                    'paid_at': item.order.paid_at.isoformat() if item.order.paid_at else None,
                    'notes': item.order.notes
                },
                'items': [],
                'vendor_total': 0
            }

        vendor_item_total = item.subtotal
        paid_orders_dict[order_id]['vendor_total'] += float(vendor_item_total)
        paid_orders_dict[order_id]['items'].append({
            'id': item.id,
            'name': item.menu_item.name,
            'quantity': item.quantity,
            'subtotal': str(item.subtotal),
            'special_instructions': item.special_instructions,
        })

    paid_orders_list = list(paid_orders_dict.values())

    # Get statistics
    today = timezone.now().date()

    # Calculate vendor-specific revenue
    today_paid_items = OrderItem.objects.filter(
        menu_item__category__vendor=vendor,
        order__status='paid',
        order__created_at__date=today
    )
    today_revenue = sum(float(item.subtotal) for item in today_paid_items)

    # Calculate unpaid revenue (delivered orders ready for payment)
    unpaid_items = OrderItem.objects.filter(
        menu_item__category__vendor=vendor,
        order__status__in=['delivered', 'ready']
    )
    unpaid_revenue = sum(float(item.subtotal) for item in unpaid_items)

    stats = {
        'pending_orders': len([o for o in orders if o['order']['status'] == 'pending']),
        'preparing_orders': len([o for o in orders if o['order']['status'] == 'preparing']),
        'ready_orders': len([o for o in orders if o['order']['status'] == 'ready']),
        'delivered_orders': len([o for o in orders if o['order']['status'] == 'delivered']),
        'paid_orders_today': len([o for o in paid_orders_list if o['order']['created_at'][:10] == str(today)]),
        'todays_orders': OrderItem.objects.filter(
            menu_item__category__vendor=vendor,
            order__created_at__date=today
        ).count(),
        'today_revenue': round(today_revenue, 2),
        'unpaid_revenue': round(unpaid_revenue, 2),
        'total_paid_orders': len(paid_orders_list)
    }

    context = {
        'vendor': vendor,
        'orders': json.dumps(orders, cls=DjangoJSONEncoder),
        'paid_orders': paid_orders_list,
        'stats': stats
    }

    # Use test template if requested, organized template by default
    if request.GET.get('test'):
        template = 'vendors/dashboard_test.html'
    elif request.GET.get('old'):
        template = 'vendors/dashboard.html'
    else:
        template = 'vendors/dashboard_organized.html'

    logger.info(f"Vendor dashboard: Using template {template} for vendor {vendor_id}")
    logger.info(f"Request path: {request.get_full_path()}")

    return render(request, template, context)

@login_required
def vendor_list(request):
    """List vendors for the user (mainly for admin/staff users)"""
    if request.user.is_staff:
        vendors = Vendor.objects.all()
    else:
        vendors = Vendor.objects.filter(owner=request.user)
        # If user has only one vendor, redirect directly to it
        if vendors.count() == 1:
            return redirect('vendors:vendor_dashboard', vendor_id=vendors.first().id)

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
def vendor_payment_report(request, vendor_id):
    """Vendor payment report page"""
    try:
        vendor = get_object_or_404(Vendor, id=vendor_id)

        # Check permission
        if vendor.owner != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to view this report')
            return redirect('vendors:vendor_dashboard', vendor_id=vendor_id)

        # Get date range from request
        from datetime import datetime, timedelta
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)  # Default to last 30 days

        if request.GET.get('start_date'):
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        if request.GET.get('end_date'):
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()

        # Get vendor items in date range
        vendor_items = OrderItem.objects.filter(
            menu_item__category__vendor=vendor,
            order__created_at__date__range=[start_date, end_date]
        ).select_related('order', 'menu_item')

        # Separate paid and unpaid
        paid_items = vendor_items.filter(order__status='paid')
        unpaid_items = vendor_items.filter(order__status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered'])

        # Calculate totals
        paid_revenue = sum(float(item.subtotal) for item in paid_items)
        unpaid_revenue = sum(float(item.subtotal) for item in unpaid_items)

        # Group by date for trend analysis
        daily_revenue = {}
        for item in paid_items:
            date_key = item.order.created_at.date().isoformat()
            if date_key not in daily_revenue:
                daily_revenue[date_key] = 0
            daily_revenue[date_key] += float(item.subtotal)

        # Top selling items
        from collections import defaultdict
        item_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0, 'orders': 0})
        order_ids = set()

        for item in paid_items:
            key = item.menu_item.name
            item_sales[key]['quantity'] += item.quantity
            item_sales[key]['revenue'] += float(item.subtotal)
            if item.order.id not in order_ids:
                item_sales[key]['orders'] += 1
                order_ids.add(item.order.id)

        top_items = sorted(
            item_sales.items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )[:10]

        # Payment method breakdown (from order notes)
        payment_methods = {'cash': 0, 'card': 0, 'mobile': 0, 'other': 0}
        for item in paid_items:
            payment_amount = float(item.subtotal)
            if 'cash' in item.order.notes.lower():
                payment_methods['cash'] += payment_amount
            elif 'card' in item.order.notes.lower():
                payment_methods['card'] += payment_amount
            elif 'mobile' in item.order.notes.lower():
                payment_methods['mobile'] += payment_amount
            else:
                payment_methods['other'] += payment_amount

        report_data = {
            'vendor_name': vendor.name,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'paid_revenue': round(paid_revenue, 2),
                'unpaid_revenue': round(unpaid_revenue, 2),
                'total_revenue': round(paid_revenue + unpaid_revenue, 2),
                'paid_orders': len(set(item.order.id for item in paid_items)),
                'unpaid_orders': len(set(item.order.id for item in unpaid_items)),
                'total_items_sold': sum(item.quantity for item in paid_items),
                'average_order_value': round(paid_revenue / len(set(item.order.id for item in paid_items)) if paid_items else 0, 2)
            },
            'daily_revenue': daily_revenue,
            'payment_methods': payment_methods,
            'top_items': [
                {
                    'name': name,
                    'quantity': data['quantity'],
                    'revenue': round(data['revenue'], 2),
                    'orders': data['orders']
                }
                for name, data in top_items
            ],
            'unpaid_orders_detail': [
                {
                    'order_id': str(item.order.id)[:8],
                    'table_number': item.order.table.number,
                    'status': item.order.status,
                    'vendor_amount': float(item.subtotal),
                    'created_at': item.order.created_at.isoformat(),
                    'customer_name': item.order.customer_name
                }
                for item in unpaid_items.order_by('-order__created_at')[:20]  # Latest 20
            ]
        }

        # Calculate max daily revenue for chart scaling
        max_daily_revenue = max(daily_revenue.values()) if daily_revenue else 0

        context = {
            'vendor': vendor,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': report_data['summary'],
            'daily_revenue': sorted(daily_revenue.items()),
            'max_daily_revenue': max_daily_revenue,
            'payment_methods': payment_methods,
            'top_items': report_data['top_items'],
            'unpaid_orders_detail': report_data['unpaid_orders_detail']
        }

        return render(request, 'vendors/payment_report.html', context)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def menu_management(request, vendor_id):
    """Manage vendor menu items"""
    vendor = get_object_or_404(Vendor, id=vendor_id)

    # Check permission
    if vendor.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to manage this vendor')
        return redirect('login')

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

@login_required
def debug_dashboard(request, vendor_id):
    """Debug version of vendor dashboard to isolate issues"""
    vendor = get_object_or_404(Vendor, id=vendor_id)

    # Check if user has permission
    if vendor.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this vendor dashboard')
        return redirect('login')

    # Get current orders for this vendor (same logic as main dashboard)
    current_orders = OrderItem.objects.filter(
        menu_item__category__vendor=vendor,
        order__status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
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

    context = {
        'vendor': vendor,
        'orders': json.dumps(orders, cls=DjangoJSONEncoder),
    }

    return render(request, 'vendors/debug_dashboard.html', context)
