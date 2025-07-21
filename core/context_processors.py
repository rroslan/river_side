from vendors.models import Category, Vendor
from orders.models import Cart, Order
from django.conf import settings

def categories(request):
    """Add categories to all templates"""
    try:
        categories = Category.objects.filter(vendor__is_active=True).select_related('vendor')
        return {'categories': categories}
    except:
        return {'categories': []}

def site_info(request):
    """Add site information to all templates"""
    return {
        'site_name': 'River Side Food Court',
        'site_description': 'Delicious food and drinks from multiple vendors',
        'debug': settings.DEBUG,
    }

def cart_info(request):
    """Add cart information to all templates"""
    try:
        if hasattr(request, 'session') and request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if cart:
                return {
                    'cart_count': cart.get_item_count(),
                    'cart_total': cart.get_total(),
                    'has_cart_items': cart.items.exists()
                }
    except:
        pass

    return {
        'cart_count': 0,
        'cart_total': 0,
        'has_cart_items': False
    }

def navigation_context(request):
    """Add navigation context to all templates"""
    current_path = request.path

    # Determine active section
    active_section = 'home'
    if '/vendors/' in current_path:
        active_section = 'vendors'
    elif '/orders/' in current_path:
        active_section = 'orders'
    elif '/admin/' in current_path:
        active_section = 'admin'

    return {
        'current_path': current_path,
        'active_section': active_section,
    }

def vendor_context(request):
    """Add vendor information to all templates"""
    try:
        vendors = Vendor.objects.filter(is_active=True)
        drinks_vendors = vendors.filter(vendor_type='drinks')
        food_vendors = vendors.filter(vendor_type='food')

        return {
            'all_vendors': vendors,
            'drinks_vendors': drinks_vendors,
            'food_vendors': food_vendors,
            'vendor_count': vendors.count()
        }
    except:
        return {
            'all_vendors': [],
            'drinks_vendors': [],
            'food_vendors': [],
            'vendor_count': 0
        }
