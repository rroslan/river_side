from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, Cart, CartItem
from vendors.models import Table, MenuItem, Vendor, Category
import json
from decimal import Decimal

def table_selection(request):
    """Landing page with menu and table selection"""
    tables = Table.objects.filter(is_active=True).order_by('number')

    # Add occupancy status to each table
    for table in tables:
        table.occupied = table.is_occupied

    # Get all vendors and their categories for the menu
    vendors = Vendor.objects.filter(is_active=True).prefetch_related(
        'categories__menu_items'
    ).order_by('vendor_type', 'name')

    # Separate drinks and food vendors
    drinks_vendors = vendors.filter(vendor_type='drinks')
    food_vendors = vendors.filter(vendor_type='food')

    # Check if user has a saved table
    saved_table = None
    if request.session.get('selected_table'):
        try:
            table_number = request.session['selected_table']
            saved_table = Table.objects.get(number=table_number, is_active=True)
        except Table.DoesNotExist:
            del request.session['selected_table']

    # Serialize vendor data for frontend
    def serialize_vendors(vendor_queryset):
        vendors_data = []
        for vendor in vendor_queryset:
            categories_data = []
            for category in vendor.categories.filter(is_active=True):
                items_data = []
                for item in category.menu_items.filter(is_available=True):
                    items_data.append({
                        'id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'price': str(item.price),
                        'is_available': item.is_available,
                        'is_vegetarian': item.is_vegetarian,
                        'is_vegan': item.is_vegan,
                        'is_spicy': item.is_spicy,
                        'calories': item.calories,
                        'preparation_time': item.preparation_time,
                        'ingredients': item.ingredients,
                        'image': item.image.url if item.image else None
                    })

                if items_data:  # Only include categories that have available items
                    categories_data.append({
                        'id': category.id,
                        'name': category.name,
                        'description': category.description,
                        'menu_items': items_data
                    })

            if categories_data:  # Only include vendors that have active categories with items
                vendors_data.append({
                    'id': vendor.id,
                    'name': vendor.name,
                    'description': vendor.description,
                    'vendor_type': vendor.vendor_type,
                    'categories': categories_data
                })

        return vendors_data

    context = {
        'tables': tables,
        'drinks_vendors': json.dumps(serialize_vendors(drinks_vendors)),
        'food_vendors': json.dumps(serialize_vendors(food_vendors)),
        'saved_table': saved_table,
    }

    return render(request, 'orders/table_selection.html', context)

def phone_input(request, table_number):
    """Phone input step after table selection"""
    # Verify table exists and is available
    table = get_object_or_404(Table, number=table_number, is_active=True)

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        customer_name = request.POST.get('customer_name', '').strip()

        if phone:
            # Store customer info in session
            request.session['selected_table'] = table_number
            request.session['customer_phone'] = phone
            request.session['customer_name'] = customer_name
            return redirect('orders:table_menu', table_number=table_number)
        else:
            messages.error(request, 'Please enter a valid phone number.')

    context = {
        'table': table,
    }

    return render(request, 'orders/phone_input.html', context)

def table_menu(request, table_number):
    """Display menu for selected table"""
    # Verify table exists and customer has provided phone
    table = get_object_or_404(Table, number=table_number, is_active=True)

    if not request.session.get('customer_phone'):
        return redirect('orders:phone_input', table_number=table_number)

    # Store selected table in session
    request.session['selected_table'] = table_number

    # Get all vendors and their categories for the menu
    vendors = Vendor.objects.filter(is_active=True).prefetch_related(
        'categories__menu_items'
    ).order_by('vendor_type', 'name')

    # Separate drinks and food vendors
    drinks_vendors = vendors.filter(vendor_type='drinks')
    food_vendors = vendors.filter(vendor_type='food')

    context = {
        'table': table,
        'drinks_vendors': drinks_vendors,
        'food_vendors': food_vendors,
        'customer_phone': request.session.get('customer_phone'),
        'customer_name': request.session.get('customer_name'),
    }

    return render(request, 'orders/simple_menu.html', context)

@require_http_methods(["POST"])
def add_to_cart(request):
    """Add item to cart via AJAX"""
    try:
        data = json.loads(request.body)
        menu_item_id = data.get('menu_item_id')
        quantity = int(data.get('quantity', 1))
        special_instructions = data.get('special_instructions', '')
        table_number = data.get('table_number')

        if not menu_item_id or not table_number:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        menu_item = get_object_or_404(MenuItem, id=menu_item_id, is_available=True)
        table = get_object_or_404(Table, number=table_number, is_active=True)

        # Store table selection in session
        request.session['selected_table'] = table_number

        # Get or create cart
        cart = get_or_create_cart(request, table)

        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            defaults={
                'quantity': quantity,
                'unit_price': menu_item.price,
                'special_instructions': special_instructions
            }
        )

        if not created:
            # Update existing item
            cart_item.quantity += quantity
            cart_item.special_instructions = special_instructions
            cart_item.save()

        return JsonResponse({
            'success': True,
            'cart_count': cart.get_item_count(),
            'cart_total': str(cart.get_total()),
            'item_name': menu_item.name,
            'quantity_added': quantity
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def update_cart_item(request):
    """Update cart item quantity"""
    try:
        data = json.loads(request.body)
        cart_item_id = data.get('cart_item_id')
        quantity = int(data.get('quantity', 1))

        if quantity < 1:
            return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)

        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({
            'success': True,
            'cart_count': cart_item.cart.get_item_count(),
            'cart_total': str(cart_item.cart.get_total()),
            'item_subtotal': str(cart_item.subtotal)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def remove_from_cart(request):
    """Remove item from cart"""
    try:
        data = json.loads(request.body)
        cart_item_id = data.get('cart_item_id')

        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart = cart_item.cart
        cart_item.delete()

        return JsonResponse({
            'success': True,
            'cart_count': cart.get_item_count(),
            'cart_total': str(cart.get_total())
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def checkout(request, table_number):
    """Checkout page - view cart items and place order"""
    table = get_object_or_404(Table, number=table_number, is_active=True)

    # Check if customer has provided phone
    if not request.session.get('customer_phone'):
        return redirect('orders:phone_input', table_number=table_number)

    cart = get_or_create_cart(request, table)

    if not cart.items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('orders:table_menu', table_number=table_number)

    # Group cart items by vendor for better display
    cart_items_by_vendor = {}
    for item in cart.items.all():
        vendor_name = item.menu_item.category.vendor.name
        if vendor_name not in cart_items_by_vendor:
            cart_items_by_vendor[vendor_name] = []
        cart_items_by_vendor[vendor_name].append(item)

    context = {
        'table': table,
        'cart': cart,
        'cart_items': cart.items.all(),
        'cart_items_by_vendor': cart_items_by_vendor,
        'cart_total': cart.get_total(),
        'cart_count': cart.get_item_count(),
        'customer_phone': request.session.get('customer_phone'),
        'customer_name': request.session.get('customer_name'),
    }

    return render(request, 'orders/checkout.html', context)

@require_http_methods(["POST"])
def place_order(request, table_number):
    """Place the order"""
    try:
        table = get_object_or_404(Table, number=table_number, is_active=True)
        cart = get_or_create_cart(request, table)

        if not cart.items.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)

        # Get customer info from session
        customer_name = request.session.get('customer_name', '')
        customer_phone = request.session.get('customer_phone', '')

        # Get notes from request body if provided
        notes = ''
        if request.body:
            try:
                data = json.loads(request.body)
                notes = data.get('notes', '')
            except json.JSONDecodeError:
                pass

        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                table=table,
                customer_name=customer_name,
                customer_phone=customer_phone,
                notes=notes,
                status='pending'
            )

            # Create order items from cart
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    special_instructions=cart_item.special_instructions
                )

            # Calculate total
            order.calculate_total()
            order.save()

            # Clear cart
            cart.items.all().delete()

            return JsonResponse({
                'success': True,
                'order_id': str(order.id),
                'redirect_url': f'/orders/track/{table_number}/'
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def track_orders(request, table_number):
    """Track orders for a table in real-time"""
    table = get_object_or_404(Table, number=table_number, is_active=True)

    # Get active orders for this table
    orders = Order.objects.filter(
        table=table,
        status__in=['pending', 'confirmed', 'preparing', 'ready']
    ).order_by('-created_at')

    context = {
        'table': table,
        'orders': orders
    }

    return render(request, 'orders/track_orders.html', context)

def order_history(request, table_number):
    """View order history for a table"""
    table = get_object_or_404(Table, number=table_number, is_active=True)

    orders = Order.objects.filter(table=table).order_by('-created_at')[:20]

    context = {
        'table': table,
        'orders': orders
    }

    return render(request, 'orders/order_history.html', context)

def get_or_create_cart(request, table):
    """Get or create cart for session and table"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        session_key=session_key,
        defaults={'table': table}
    )

    # Update table if different
    if cart.table != table:
        cart.table = table
        cart.save()

    return cart

@require_http_methods(["GET"])
def get_cart_status(request, table_number):
    """Get current cart status"""
    try:
        table = get_object_or_404(Table, number=table_number, is_active=True)
        cart = get_or_create_cart(request, table)

        return JsonResponse({
            'cart_count': cart.get_item_count(),
            'cart_total': str(cart.get_total())
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_table_items_status(request, table_number):
    """Get comprehensive items status including cart and orders"""
    try:
        table = get_object_or_404(Table, number=table_number, is_active=True)

        # Get cart items - handle missing session gracefully
        cart_items = []
        cart_count = 0
        cart_total = "0.00"

        try:
            cart = get_or_create_cart(request, table)
            for item in cart.items.all():
                cart_items.append({
                    'id': item.id,
                    'name': item.menu_item.name,
                    'vendor_name': item.menu_item.category.vendor.name,
                    'quantity': item.quantity,
                    'unit_price': str(item.unit_price),
                    'subtotal': str(item.subtotal),
                    'special_instructions': item.special_instructions,
                    'type': 'cart'
                })
            cart_count = cart.get_item_count()
            cart_total = str(cart.get_total())
        except Exception as cart_error:
            # If cart fails due to session issues, continue with empty cart
            print(f"Cart error: {cart_error}")

        # Get active orders for this table
        orders = Order.objects.filter(
            table=table,
            status__in=['pending', 'confirmed', 'preparing', 'ready']
        ).order_by('-created_at')

        orders_data = []
        for order in orders:
            items_data = []
            for item in order.items.all():
                items_data.append({
                    'id': item.id,
                    'name': item.menu_item.name,
                    'vendor_name': item.menu_item.category.vendor.name,
                    'quantity': item.quantity,
                    'unit_price': str(item.unit_price),
                    'subtotal': str(item.subtotal),
                    'special_instructions': item.special_instructions,
                    'status': item.status
                })

            orders_data.append({
                'id': str(order.id),
                'status': order.status,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.isoformat(),
                'estimated_ready_time': order.estimated_ready_time.isoformat() if order.estimated_ready_time else None,
                'items': items_data,
                'notes': order.notes
            })

        return JsonResponse({
            'cart': {
                'items': cart_items,
                'count': cart_count,
                'total': cart_total
            },
            'orders': orders_data,
            'table_number': table.number
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def status_check(request):
    """Simple status check endpoint"""
    try:
        # Check if database is accessible
        table_count = Table.objects.count()
        vendor_count = Vendor.objects.count()
        menu_item_count = MenuItem.objects.count()

        return JsonResponse({
            'status': 'ok',
            'tables': table_count,
            'vendors': vendor_count,
            'menu_items': menu_item_count,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

def get_tables(request):
    """Get all tables for API"""
    try:
        tables = Table.objects.filter(is_active=True).order_by('number')
        tables_data = []
        for table in tables:
            tables_data.append({
                'number': table.number,
                'seats': table.seats,
                'occupied': table.is_occupied,
                'is_active': table.is_active
            })
        return JsonResponse({'tables': tables_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def clear_session(request):
    """Clear customer session data and cart"""
    try:
        # Get table number from session before clearing
        table_number = request.session.get('selected_table')

        # Clear server-side cart if table exists
        if table_number:
            try:
                table = Table.objects.get(number=table_number, is_active=True)
                cart = get_or_create_cart(request, table)
                # Delete all cart items
                cart.items.all().delete()
            except Table.DoesNotExist:
                pass  # Table doesn't exist, nothing to clear

        # Clear session data
        session_keys = ['selected_table', 'customer_phone', 'customer_name']
        for key in session_keys:
            if key in request.session:
                del request.session[key]

        request.session.modified = True

        return JsonResponse({'success': True, 'message': 'Session and cart cleared'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def debug_cart(request, table_number):
    """Debug endpoint to check cart contents"""
    try:
        table = get_object_or_404(Table, number=table_number, is_active=True)
        cart = get_or_create_cart(request, table)

        cart_items = []
        for item in cart.items.all():
            cart_items.append({
                'id': item.id,
                'menu_item': item.menu_item.name,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'subtotal': str(item.subtotal),
                'special_instructions': item.special_instructions
            })

        return JsonResponse({
            'cart_id': cart.id,
            'session_key': cart.session_key,
            'table_number': table.number,
            'total_items': cart.get_item_count(),
            'total_amount': str(cart.get_total()),
            'cart_items': cart_items,
            'session_data': {
                'selected_table': request.session.get('selected_table'),
                'customer_phone': request.session.get('customer_phone'),
                'customer_name': request.session.get('customer_name')
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def clear_cart(request, table_number):
    """Clear cart for debugging purposes"""
    try:
        table = get_object_or_404(Table, number=table_number, is_active=True)
        cart = get_or_create_cart(request, table)

        # Delete all cart items
        cart.items.all().delete()

        return JsonResponse({
            'success': True,
            'message': f'Cart cleared for table {table_number}',
            'cart_count': cart.get_item_count(),
            'cart_total': str(cart.get_total())
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
