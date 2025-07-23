from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.management import call_command
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.admin import AdminSite
import io
from contextlib import redirect_stdout


class DataResetAdminView(View):
    """Custom admin view for resetting demo data"""

    @method_decorator(staff_member_required)
    def get(self, request):
        """Show the data reset confirmation page"""
        context = {
            'title': 'Reset Demo Data',
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
            'has_permission': True,
        }
        return render(request, 'admin/data_reset.html', context)

    @method_decorator(staff_member_required)
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Execute the data reset command"""
        if request.headers.get('Content-Type') == 'application/json':
            # AJAX request for real-time output
            try:
                # Capture command output
                output_buffer = io.StringIO()

                with redirect_stdout(output_buffer):
                    call_command('reset_demo_data', '--force')

                output = output_buffer.getvalue()

                return JsonResponse({
                    'success': True,
                    'message': 'Data reset completed successfully!',
                    'output': output
                })

            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error during reset: {str(e)}',
                    'output': str(e)
                })
        else:
            # Regular form submission
            try:
                call_command('reset_demo_data', '--force')
                messages.success(request, '🎉 Demo data has been reset successfully!')

            except Exception as e:
                messages.error(request, f'❌ Error during reset: {str(e)}')

            return redirect('admin:data_reset')


class StatsAPIView(View):
    """API view to get quick stats for admin dashboard"""

    @method_decorator(staff_member_required)
    def get(self, request):
        """Return quick stats as JSON"""
        from django.utils import timezone
        from vendors.models import Table
        from orders.models import Order

        today = timezone.now().date()

        stats = {
            'orders_today': Order.objects.filter(created_at__date=today).count(),
            'unpaid_orders': Order.objects.filter(status__in=['delivered', 'ready']).count(),
            'active_tables': Table.objects.filter(
                orders__status__in=['pending', 'confirmed', 'preparing']
            ).distinct().count(),
            'total_orders': Order.objects.count(),
        }

        return JsonResponse(stats)


# Extend the default admin site with custom URLs
def get_custom_admin_urls():
    """Add custom URLs to the existing admin site"""
    from django.urls import path

    custom_urls = [
        path('data-reset/', DataResetAdminView.as_view(), name='data_reset'),
        path('api/stats/', StatsAPIView.as_view(), name='stats_api'),
    ]
    return custom_urls


# Monkey patch the admin site to add our URLs
original_get_urls = admin.site.get_urls


def enhanced_get_urls():
    """Enhanced get_urls method that includes our custom URLs"""
    urls = original_get_urls()
    custom_urls = get_custom_admin_urls()
    return custom_urls + urls


# Apply the monkey patch
admin.site.get_urls = enhanced_get_urls


# Enhance the admin site with custom index method
original_index = admin.site.index


def enhanced_index(request, extra_context=None):
    """Enhanced index method that adds demo data management context"""
    from django.utils import timezone
    from vendors.models import Table
    from orders.models import Order

    extra_context = extra_context or {}
    extra_context['show_data_reset'] = True

    # Add real stats to context
    today = timezone.now().date()
    extra_context.update({
        'orders_today': Order.objects.filter(created_at__date=today).count(),
        'unpaid_orders': Order.objects.filter(status__in=['delivered', 'ready']).count(),
        'active_tables': Table.objects.filter(
            orders__status__in=['pending', 'confirmed', 'preparing']
        ).distinct().count(),
        'total_orders': Order.objects.count(),
    })

    return original_index(request, extra_context)


# Apply the index enhancement
admin.site.index = enhanced_index


# Customize admin site properties
admin.site.site_header = 'River Side Food Court Admin'
admin.site.site_title = 'River Side Admin'
admin.site.index_title = 'Welcome to River Side Food Court Administration'


# Admin action for resetting data from any model admin
def reset_demo_data_action(modeladmin, request, queryset):
    """Admin action to reset demo data"""
    try:
        call_command('reset_demo_data', '--force')
        messages.success(request, '🎉 Demo data has been reset successfully!')
    except Exception as e:
        messages.error(request, f'❌ Error during reset: {str(e)}')


# Set the action description
reset_demo_data_action.short_description = "🔄 Reset All Demo Data"
