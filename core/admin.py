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
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from core.permissions import CashierPermissions
import io
from contextlib import redirect_stdout


class CashierCreationForm(UserCreationForm):
    """Custom form for creating cashier users"""
    email = forms.EmailField(required=True, help_text="Email address for the cashier")
    first_name = forms.CharField(max_length=30, required=False, help_text="First name")
    last_name = forms.CharField(max_length=30, required=False, help_text="Last name")
    add_to_cashier_group = forms.BooleanField(
        initial=True,
        required=False,
        help_text="Automatically add user to Cashier group"
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

            # Add to cashier group if requested
            if self.cleaned_data["add_to_cashier_group"]:
                CashierPermissions.add_user_to_cashier_group(user)

        return user


class CashierUserAdmin(BaseUserAdmin):
    """Enhanced User admin with cashier management features"""

    add_form = CashierCreationForm

    # Add cashier-specific fields to the list display
    list_display = BaseUserAdmin.list_display + ('is_cashier', 'cashier_permissions_status')
    list_filter = BaseUserAdmin.list_filter + ('groups',)

    # Override add_fieldsets to include cashier form fields
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'add_to_cashier_group'),
        }),
    )

    actions = ['add_to_cashier_group', 'remove_from_cashier_group', 'check_cashier_permissions']

    def is_cashier(self, obj):
        """Check if user is a cashier"""
        return CashierPermissions.is_cashier(obj)
    is_cashier.boolean = True
    is_cashier.short_description = 'Is Cashier'

    def cashier_permissions_status(self, obj):
        """Show cashier permissions status"""
        if CashierPermissions.is_cashier(obj):
            status = CashierPermissions.check_cashier_permissions(obj)
            if status['has_all_permissions']:
                return "✅ Complete"
            else:
                return f"❌ Missing {len(status['missing_permissions'])}"
        return "➖ Not Cashier"
    cashier_permissions_status.short_description = 'Permissions'

    def get_form(self, request, obj=None, **kwargs):
        """Override form to show cashier info in help text"""
        form = super().get_form(request, obj, **kwargs)
        if obj and hasattr(form, 'base_fields'):
            # Add help text about cashier status
            if CashierPermissions.is_cashier(obj):
                status = CashierPermissions.check_cashier_permissions(obj)
                cashier_info = f"Cashier Status: {'Complete' if status['has_all_permissions'] else 'Incomplete'} permissions"
            else:
                cashier_info = "Not a cashier user"

            # Add this info to the username field help text
            if 'username' in form.base_fields:
                form.base_fields['username'].help_text = f"Current status: {cashier_info}"

        return form

    # Custom admin actions
    def add_to_cashier_group(self, request, queryset):
        """Add selected users to cashier group"""
        added_count = 0
        for user in queryset:
            if not CashierPermissions.is_cashier(user):
                result = CashierPermissions.add_user_to_cashier_group(user)
                if result['success']:
                    added_count += 1

        if added_count > 0:
            self.message_user(request, f"Successfully added {added_count} users to Cashier group.", messages.SUCCESS)
        else:
            self.message_user(request, "No users were added (they may already be cashiers).", messages.WARNING)
    add_to_cashier_group.short_description = "➕ Add selected users to Cashier group"

    def remove_from_cashier_group(self, request, queryset):
        """Remove selected users from cashier group"""
        removed_count = 0
        for user in queryset:
            if CashierPermissions.is_cashier(user) and not user.is_superuser:
                result = CashierPermissions.remove_user_from_cashier_group(user)
                if result['success']:
                    removed_count += 1

        if removed_count > 0:
            self.message_user(request, f"Successfully removed {removed_count} users from Cashier group.", messages.SUCCESS)
        else:
            self.message_user(request, "No users were removed (they may not be cashiers or are superusers).", messages.WARNING)
    remove_from_cashier_group.short_description = "➖ Remove selected users from Cashier group"

    def check_cashier_permissions(self, request, queryset):
        """Check permissions for selected cashier users"""
        results = []
        for user in queryset:
            if CashierPermissions.is_cashier(user):
                status = CashierPermissions.check_cashier_permissions(user)
                if status['has_all_permissions']:
                    results.append(f"✅ {user.username}: All permissions OK")
                else:
                    results.append(f"❌ {user.username}: Missing {len(status['missing_permissions'])} permissions")
            else:
                results.append(f"➖ {user.username}: Not a cashier")

        message = "\n".join(results)
        self.message_user(request, f"Permission check results:\n{message}", messages.INFO)
    check_cashier_permissions.short_description = "🔍 Check cashier permissions"


class CashierManagementView(View):
    """Custom admin view for cashier management"""

    @method_decorator(staff_member_required)
    def get(self, request):
        """Show the cashier management page"""
        # Get cashier statistics
        cashier_group = Group.objects.filter(name='Cashier').first()
        cashier_users = User.objects.filter(groups=cashier_group) if cashier_group else User.objects.none()

        # Check permissions for all cashiers
        cashier_data = []
        for user in cashier_users:
            status = CashierPermissions.check_cashier_permissions(user)
            cashier_data.append({
                'user': user,
                'status': status,
                'has_issues': not status['has_all_permissions'] or status['forbidden_permissions_held']
            })

        context = {
            'title': 'Cashier Management',
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
            'has_permission': True,
            'cashier_group': cashier_group,
            'cashier_users': cashier_data,
            'total_cashiers': len(cashier_data),
            'users_with_issues': sum(1 for data in cashier_data if data['has_issues']),
        }
        return render(request, 'admin/cashier_management.html', context)

    @method_decorator(staff_member_required)
    def post(self, request):
        """Handle cashier management actions"""
        action = request.POST.get('action')

        if action == 'setup_permissions':
            try:
                call_command('setup_cashier_permissions', '--reset')
                messages.success(request, '✅ Cashier permissions have been set up successfully!')
            except Exception as e:
                messages.error(request, f'❌ Error setting up permissions: {str(e)}')

        elif action == 'audit_users':
            try:
                call_command('manage_cashier_users', 'audit', '--fix-issues')
                messages.success(request, '✅ Cashier user audit completed with automatic fixes!')
            except Exception as e:
                messages.error(request, f'❌ Error during audit: {str(e)}')

        elif action == 'remove_from_group':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(pk=user_id)
                if not user.is_superuser:
                    result = CashierPermissions.remove_user_from_cashier_group(user)
                    if result['success']:
                        messages.success(request, f'✅ Removed {user.username} from Cashier group!')
                    else:
                        messages.error(request, f'❌ Error: {result["message"]}')
                else:
                    messages.warning(request, '⚠️ Cannot remove superuser from cashier access.')
            except User.DoesNotExist:
                messages.error(request, '❌ User not found.')
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')

        return redirect('admin:cashier_management')


class QuickCashierCreationView(View):
    """Quick cashier creation view for admin"""

    @method_decorator(staff_member_required)
    def get(self, request):
        """Show quick cashier creation form"""
        context = {
            'title': 'Quick Cashier Creation',
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
            'has_permission': True,
        }
        return render(request, 'admin/quick_cashier_creation.html', context)

    @method_decorator(staff_member_required)
    def post(self, request):
        """Handle quick cashier creation"""
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, '❌ Username and password are required.')
            return redirect('admin:quick_cashier_creation')

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, f'❌ User "{username}" already exists.')
                return redirect('admin:quick_cashier_creation')

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Add to cashier group
            result = CashierPermissions.add_user_to_cashier_group(user)
            if result['success']:
                messages.success(request, f'✅ Successfully created cashier: {username}')
                messages.info(request, f'📋 Credentials: {username} / {password}')
            else:
                messages.warning(request, f'⚠️ User created but group assignment failed: {result["message"]}')

        except Exception as e:
            messages.error(request, f'❌ Error creating user: {str(e)}')

        return redirect('admin:cashier_management')


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
        path('cashier-management/', CashierManagementView.as_view(), name='cashier_management'),
        path('quick-cashier/', QuickCashierCreationView.as_view(), name='quick_cashier_creation'),
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
    extra_context['show_cashier_management'] = True

    # Add real stats to context
    today = timezone.now().date()

    # Get cashier statistics
    cashier_group = Group.objects.filter(name='Cashier').first()
    total_cashiers = User.objects.filter(groups=cashier_group).count() if cashier_group else 0

    extra_context.update({
        'orders_today': Order.objects.filter(created_at__date=today).count(),
        'unpaid_orders': Order.objects.filter(status__in=['delivered', 'ready']).count(),
        'active_tables': Table.objects.filter(
            orders__status__in=['pending', 'confirmed', 'preparing']
        ).distinct().count(),
        'total_orders': Order.objects.count(),
        'total_cashiers': total_cashiers,
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


# Unregister the default User admin and register our enhanced one
admin.site.unregister(User)
admin.site.register(User, CashierUserAdmin)
