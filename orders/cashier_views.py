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
from core.permissions import CashierPermissions, cashier_required, cashier_permission_required
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def is_cashier_or_staff(user):
    """Check if user is staff or has cashier permissions"""
    return user.is_staff or CashierPermissions.is_cashier(user)

def cashier_login_required(view_func):
    """Custom login required decorator that redirects to cashier login"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to cashier view: {request.path}")
            from django.shortcuts import redirect
            login_url = reverse('orders:cashier_login')
            path = request.get_full_path()
            return redirect(f'{login_url}?next={path}')

        if not is_cashier_or_staff(request.user):
            logger.warning(f"Non-cashier user {request.user.username} attempted to access cashier view: {request.path}")
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.error(request, 'You do not have permission to access the cashier dashboard.')
            return redirect('orders:cashier_login')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def cashier_login(request):
    """Cashier login page"""
    if request.user.is_authenticated and is_cashier_or_staff(request.user):
        logger.info(f"Already authenticated cashier {request.user.username} redirected to dashboard")
        return redirect('orders:cashier_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_active:
                    if is_cashier_or_staff(user):
                        login(request, user)
                        logger.info(f"Successful cashier login: {username}")

                        # Check permissions status
                        perm_status = CashierPermissions.check_cashier_permissions(user)
                        if not perm_status['has_all_permissions']:
                            logger.warning(f"Cashier {username} missing permissions: {perm_status['missing_permissions']}")
                            messages.warning(request, 'Some permissions may be missing. Contact administrator if you experience issues.')

                        next_url = request.GET.get('next')
                        if next_url:
                            return redirect(next_url)
                        return redirect('orders:cashier_dashboard')
                    else:
                        logger.warning(f"Non-cashier user {username} attempted login")
                        messages.error(request, 'You do not have cashier permissions.')
                else:
                    logger.warning(f"Inactive user {username} attempted login")
                    messages.error(request, 'Your account is inactive.')
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')

    return render(request, 'orders/cashier_login.html')

def cashier_logout(request):
    """Cashier logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('orders:cashier_login')

@cashier_login_required
def cashier_dashboard(request):
    """Main cashier dashboard showing orders ready for payment"""
    logger.info(f"Cashier {request.user.username} accessed dashboard")

    # Check user permissions and log any issues
    perm_status = CashierPermissions.check_cashier_permissions(request.user)
    if not perm_status['has_all_permissions']:
        logger.warning(f"Cashier {request.user.username} has incomplete permissions: {perm_status['missing_permissions']}")
        messages.warning(request, f"You may be missing some permissions. Contact administrator if you experience issues.")

    # Get filters from request
    status_filter = request.GET.get('status', 'delivered')
    table_filter = request.GET.get('table', '')
    date_filter = request.GET.get('date', 'today')

    # Base query for orders - check permission
    if not request.user.has_perm('orders.view_order'):
        logger.error(f"User {request.user.username} lacks orders.view_order permission")
        messages.error(request, "You don't have permission to view orders.")
        return redirect('orders:cashier_login')

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

    # Add user permission info to context
    context = {
        'orders': page_obj,
        'stats': stats,
        'status_filter': status_filter,
        'table_filter': table_filter,
        'date_filter': date_filter,
        'user_permissions': perm_status,
        'can_change_orders': request.user.has_perm('orders.change_order'),
        'can_reset_tables': request.user.has_perm('vendors.change_table'),
    }

    # Get all active tables for filter dropdown
    active_tables = Table.objects.filter(is_active=True).order_by('number')

    # Get vendor payment breakdown
    vendor_breakdown = []
    from vendors.models import Vendor
    for vendor in Vendor.objects.all():
        # Calculate vendor-specific revenue for today
        vendor_paid_items = OrderItem.objects.filter(
            menu_item__category__vendor=vendor,
            order__status='paid',
            order__created_at__date=today
        )
        vendor_unpaid_items = OrderItem.objects.filter(
            menu_item__category__vendor=vendor,
            order__status__in=['delivered', 'ready']
        )

        paid_revenue = sum(float(item.subtotal) for item in vendor_paid_items)
        unpaid_revenue = sum(float(item.subtotal) for item in vendor_unpaid_items)

        if paid_revenue > 0 or unpaid_revenue > 0:
            vendor_breakdown.append({
                'vendor': vendor,
                'paid_revenue': round(paid_revenue, 2),
                'unpaid_revenue': round(unpaid_revenue, 2),
                'total_revenue': round(paid_revenue + unpaid_revenue, 2),
                'paid_orders': len(set(item.order.id for item in vendor_paid_items)),
                'unpaid_orders': len(set(item.order.id for item in vendor_unpaid_items))
            })

    context = {
        'page_obj': page_obj,
        'stats': stats,
        'active_tables': active_tables,
        'vendor_breakdown': vendor_breakdown,
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
    logger.info(f"Cashier {request.user.username} attempting to mark order {order_id} as paid")

    try:
        order = get_object_or_404(Order, id=order_id)

        # Check specific permission for this action
        if not request.user.has_perm('orders.change_order'):
            logger.error(f"User {request.user.username} lacks permission to mark orders as paid")
            return JsonResponse({
                'error': 'You do not have permission to mark orders as paid'
            }, status=403)

        # Validate order can be marked as paid
        if order.status not in ['delivered', 'ready']:
            logger.warning(f"Order {order_id} cannot be paid - status: {order.status}")
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
    logger.info(f"Cashier {request.user.username} attempting to reset table {table_number}")

    try:
        # Check specific permission for this action
        if not request.user.has_perm('vendors.change_table'):
            logger.error(f"User {request.user.username} lacks permission to reset tables")
            return JsonResponse({
                'error': 'You do not have permission to reset tables'
            }, status=403)

        table = get_object_or_404(Table, number=table_number, is_active=True)

        # Find unpaid orders for this table
        unpaid_orders = Order.objects.filter(
            table=table,
            status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
        )

        if not unpaid_orders.exists():
            logger.info(f"Table {table_number} already clear - no orders to cancel")
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

            # Log the cancellation
            logger.info(f"Order {order.id} cancelled by {request.user.username} during table {table_number} reset")

            cancelled_count += 1
            cancelled_orders.append({
                'id': str(order.id)[:8],
                'old_status': old_status,
                'total_amount': str(order.total_amount)
            })

        logger.info(f"Table {table_number} successfully reset by {request.user.username} - {cancelled_count} orders cancelled")

        return JsonResponse({
            'success': True,
            'message': f'Table {table_number} has been reset',
            'orders_cancelled': cancelled_count,
            'cancelled_orders': cancelled_orders,
            'table_number': table_number
        })

    except Exception as e:
        logger.error(f"Error resetting table {table_number}: {str(e)}")
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
