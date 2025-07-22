from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from functools import wraps
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Order, OrderItem, OrderStatus
from vendors.models import Table, Vendor
import json
from datetime import datetime, timedelta

def is_cashier_or_staff(user):
    """Check if user is staff or has cashier permissions"""
    return user.is_staff or user.groups.filter(name='Cashiers').exists()

def cashier_login_required(view_func):
    """Custom login required decorator that redirects to cashier login"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            login_url = reverse('orders:cashier_login')
            path = request.get_full_path()
            return redirect(f'{login_url}?next={path}')

        if not is_cashier_or_staff(request.user):
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.error(request, 'You do not have permission to access the cashier dashboard.')
            return redirect('orders:cashier_login')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def cashier_login(request):
    """Cashier login page"""
    if request.user.is_authenticated and is_cashier_or_staff(request.user):
        return redirect('orders:cashier_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None and is_cashier_or_staff(user):
                login(request, user)
                next_url = request.GET.get('next', '/cashier/')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid credentials or insufficient permissions.')
        else:
            messages.error(request, 'Please enter both username and password.')

    return render(request, 'orders/cashier_login.html')

def cashier_logout(request):
    """Cashier logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('orders:cashier_login')

@cashier_login_required
def cashier_dashboard(request):
    """Main cashier dashboard showing orders ready for payment"""
    # Get filters from request
    status_filter = request.GET.get('status', 'delivered')
    table_filter = request.GET.get('table', '')
    date_filter = request.GET.get('date', 'today')

    # Base query for orders
    orders = Order.objects.select_related('table').prefetch_related('items__menu_item')

    # Apply status filter
    if status_filter == 'unpaid':
        orders = orders.filter(status__in=['delivered', 'ready'])
    elif status_filter == 'paid':
        orders = orders.filter(status='paid')
    elif status_filter:
        orders = orders.filter(status=status_filter)

    # Apply table filter
    if table_filter:
        orders = orders.filter(table__number=table_filter)

    # Apply date filter
    today = timezone.now().date()
    if date_filter == 'today':
        orders = orders.filter(created_at__date=today)
    elif date_filter == 'yesterday':
        yesterday = today - timedelta(days=1)
        orders = orders.filter(created_at__date=yesterday)
    elif date_filter == 'week':
        week_ago = today - timedelta(days=7)
        orders = orders.filter(created_at__date__gte=week_ago)

    # Order by most recent
    orders = orders.order_by('-created_at')

    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate statistics
    stats = {
        'total_orders_today': Order.objects.filter(created_at__date=today).count(),
        'unpaid_orders': Order.objects.filter(status__in=['delivered', 'ready']).count(),
        'paid_orders_today': Order.objects.filter(status='paid', created_at__date=today).count(),
        'total_revenue_today': Order.objects.filter(
            status='paid',
            created_at__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
        'active_tables': Table.objects.filter(
            orders__status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
        ).distinct().count()
    }

    # Get all active tables for filter dropdown
    active_tables = Table.objects.filter(is_active=True).order_by('number')

    context = {
        'page_obj': page_obj,
        'stats': stats,
        'active_tables': active_tables,
        'current_filters': {
            'status': status_filter,
            'table': table_filter,
            'date': date_filter,
        },
        'status_choices': OrderStatus.choices,
    }

    return render(request, 'orders/cashier_dashboard.html', context)

@cashier_login_required
@require_http_methods(["POST"])
def mark_order_paid(request, order_id):
    """Mark an order as paid"""
    try:
        order = get_object_or_404(Order, id=order_id)

        # Validate order can be marked as paid
        if order.status not in ['delivered', 'ready']:
            return JsonResponse({
                'error': f'Cannot mark order as paid. Current status: {order.status}'
            }, status=400)

        # Parse payment data
        data = json.loads(request.body)
        payment_method = data.get('payment_method', 'cash')
        payment_amount = data.get('payment_amount')
        notes = data.get('notes', '')

        # Validate payment amount
        if payment_amount:
            try:
                payment_amount = float(payment_amount)
                if payment_amount < float(order.total_amount):
                    return JsonResponse({
                        'error': f'Payment amount (${payment_amount}) is less than order total (${order.total_amount})'
                    }, status=400)
            except ValueError:
                return JsonResponse({'error': 'Invalid payment amount'}, status=400)

        # Update order status
        old_status = order.status
        order.status = OrderStatus.PAID
        order.paid_at = timezone.now()

        # Add payment notes if provided
        if notes:
            order.notes += f"\n[PAYMENT] {payment_method.upper()}: {notes}"
        else:
            order.notes += f"\n[PAYMENT] Method: {payment_method.upper()}"

        order.save()

        return JsonResponse({
            'success': True,
            'message': f'Order marked as paid via {payment_method}',
            'order_id': str(order.id),
            'old_status': old_status,
            'new_status': order.status,
            'paid_at': order.paid_at.isoformat(),
            'total_amount': str(order.total_amount)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@cashier_login_required
@require_http_methods(["POST"])
def reset_table(request, table_number):
    """Reset/clear a table by cancelling unpaid orders"""
    try:
        table = get_object_or_404(Table, number=table_number, is_active=True)

        # Find unpaid orders for this table
        unpaid_orders = Order.objects.filter(
            table=table,
            status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
        )

        if not unpaid_orders.exists():
            return JsonResponse({
                'message': f'Table {table_number} is already clear',
                'orders_cancelled': 0
            })

        # Get cancellation reason
        data = json.loads(request.body) if request.body else {}
        reason = data.get('reason', 'Table reset by cashier')

        # Cancel all unpaid orders
        cancelled_count = 0
        cancelled_orders = []

        for order in unpaid_orders:
            old_status = order.status
            order.status = OrderStatus.CANCELLED
            order.notes += f"\n[CANCELLED] {reason} - by {request.user.username}"
            order.save()

            cancelled_count += 1
            cancelled_orders.append({
                'id': str(order.id)[:8],
                'old_status': old_status,
                'total_amount': str(order.total_amount)
            })

        return JsonResponse({
            'success': True,
            'message': f'Table {table_number} has been reset',
            'orders_cancelled': cancelled_count,
            'cancelled_orders': cancelled_orders,
            'table_number': table_number
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@cashier_login_required
def order_details(request, order_id):
    """Get detailed order information for cashier review"""
    try:
        order = get_object_or_404(Order, id=order_id)

        # Serialize order data
        items_data = []
        for item in order.items.all():
            items_data.append({
                'id': item.id,
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'subtotal': str(item.subtotal),
                'special_instructions': item.special_instructions,
                'vendor': item.menu_item.category.vendor.name,
                'category': item.menu_item.category.name
            })

        order_data = {
            'id': str(order.id),
            'short_id': str(order.id)[:8],
            'table_number': order.table.number,
            'status': order.status,
            'total_amount': str(order.total_amount),
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'notes': order.notes,
            'created_at': order.created_at.isoformat(),
            'confirmed_at': order.confirmed_at.isoformat() if order.confirmed_at else None,
            'ready_at': order.ready_at.isoformat() if order.ready_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
            'paid_at': order.paid_at.isoformat() if order.paid_at else None,
            'items': items_data,
            'item_count': order.items.count(),
            'can_mark_paid': order.status in ['delivered', 'ready']
        }

        return JsonResponse(order_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@cashier_login_required
def table_status_overview(request):
    """Get overview of all table statuses"""
    try:
        tables_data = []

        for table in Table.objects.filter(is_active=True).order_by('number'):
            # Get current orders for this table
            current_orders = Order.objects.filter(
                table=table,
                status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
            ).order_by('-created_at')

            # Calculate table status
            if not current_orders.exists():
                table_status = 'available'
                latest_order = None
            else:
                latest_order = current_orders.first()
                if current_orders.filter(status__in=['delivered', 'ready']).exists():
                    table_status = 'ready_for_payment'
                elif current_orders.filter(status__in=['preparing', 'confirmed']).exists():
                    table_status = 'occupied'
                else:
                    table_status = 'pending'

            # Calculate total unpaid amount
            unpaid_total = current_orders.aggregate(
                total=Sum('total_amount')
            )['total'] or 0

            tables_data.append({
                'number': table.number,
                'seats': table.seats,
                'status': table_status,
                'orders_count': current_orders.count(),
                'unpaid_total': str(unpaid_total),
                'latest_order': {
                    'id': str(latest_order.id)[:8] if latest_order else None,
                    'status': latest_order.status if latest_order else None,
                    'created_at': latest_order.created_at.isoformat() if latest_order else None,
                    'customer_name': latest_order.customer_name if latest_order else None
                } if latest_order else None
            })

        return JsonResponse({
            'tables': tables_data,
            'summary': {
                'total_tables': len(tables_data),
                'available': len([t for t in tables_data if t['status'] == 'available']),
                'occupied': len([t for t in tables_data if t['status'] in ['occupied', 'pending']]),
                'ready_for_payment': len([t for t in tables_data if t['status'] == 'ready_for_payment'])
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@cashier_login_required
def daily_sales_report(request):
    """Generate daily sales report for cashier"""
    try:
        # Get date from request or use today
        date_str = request.GET.get('date')
        if date_str:
            report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            report_date = timezone.now().date()

        # Get orders for the specified date
        orders = Order.objects.filter(
            created_at__date=report_date
        ).select_related('table').prefetch_related('items__menu_item')

        # Calculate statistics
        total_orders = orders.count()
        paid_orders = orders.filter(status='paid')
        pending_payment = orders.filter(status__in=['delivered', 'ready'])
        cancelled_orders = orders.filter(status='cancelled')

        total_revenue = paid_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        pending_amount = pending_payment.aggregate(total=Sum('total_amount'))['total'] or 0

        # Payment method breakdown (from order notes)
        payment_methods = {}
        for order in paid_orders:
            if 'PAYMENT' in order.notes:
                if 'cash' in order.notes.lower():
                    payment_methods['cash'] = payment_methods.get('cash', 0) + float(order.total_amount)
                elif 'card' in order.notes.lower():
                    payment_methods['card'] = payment_methods.get('card', 0) + float(order.total_amount)
                else:
                    payment_methods['other'] = payment_methods.get('other', 0) + float(order.total_amount)

        # Top selling items
        from collections import defaultdict
        item_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0})

        for order in paid_orders:
            for item in order.items.all():
                key = item.menu_item.name
                item_sales[key]['quantity'] += item.quantity
                item_sales[key]['revenue'] += float(item.subtotal)

        top_items = sorted(
            item_sales.items(),
            key=lambda x: x[1]['quantity'],
            reverse=True
        )[:10]

        report_data = {
            'date': report_date.isoformat(),
            'summary': {
                'total_orders': total_orders,
                'paid_orders': paid_orders.count(),
                'pending_payment': pending_payment.count(),
                'cancelled_orders': cancelled_orders.count(),
                'total_revenue': str(total_revenue),
                'pending_amount': str(pending_amount),
                'average_order_value': str(total_revenue / paid_orders.count() if paid_orders.count() > 0 else 0)
            },
            'payment_methods': payment_methods,
            'top_items': [
                {
                    'name': name,
                    'quantity': data['quantity'],
                    'revenue': str(data['revenue'])
                }
                for name, data in top_items
            ]
        }

        return JsonResponse(report_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
