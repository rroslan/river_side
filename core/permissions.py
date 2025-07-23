from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CashierPermissions:
    """
    Utility class for managing and checking cashier permissions
    """

    # Define the core permissions needed for cashiers
    REQUIRED_PERMISSIONS = [
        # Orders management
        'orders.view_order',
        'orders.change_order',
        'orders.view_orderitem',
        'orders.change_orderitem',
        'orders.view_orderstatushistory',
        'orders.add_orderstatushistory',

        # Cart management
        'orders.view_cart',
        'orders.change_cart',
        'orders.delete_cart',
        'orders.view_cartitem',
        'orders.change_cartitem',
        'orders.delete_cartitem',

        # Vendor and menu access
        'vendors.view_vendor',
        'vendors.view_category',
        'vendors.view_menuitem',

        # Table management
        'vendors.view_table',
        'vendors.change_table',

        # Basic user viewing
        'auth.view_user',
        'auth.view_group',
    ]

    # Permissions that cashiers should NOT have
    FORBIDDEN_PERMISSIONS = [
        'auth.add_user',
        'auth.change_user',
        'auth.delete_user',
        'vendors.add_vendor',
        'vendors.change_vendor',
        'vendors.delete_vendor',
        'vendors.add_menuitem',
        'vendors.change_menuitem',
        'vendors.delete_menuitem',
        'orders.delete_order',
        'orders.delete_orderitem',
    ]

    @classmethod
    def get_cashier_group(cls):
        """Get or create the Cashier group"""
        group, created = Group.objects.get_or_create(name='Cashier')
        return group

    @classmethod
    def is_cashier(cls, user):
        """Check if a user is a cashier"""
        if not user or not user.is_authenticated:
            return False

        return user.groups.filter(name='Cashier').exists() or user.is_superuser

    @classmethod
    def check_cashier_permissions(cls, user):
        """
        Check if a user has all required cashier permissions
        Returns a dict with permission status
        """
        if not user or not user.is_authenticated:
            return {
                'is_cashier': False,
                'has_all_permissions': False,
                'missing_permissions': cls.REQUIRED_PERMISSIONS,
                'forbidden_permissions_held': [],
                'error': 'User not authenticated'
            }

        # Check if user is in cashier group
        is_cashier = cls.is_cashier(user)

        # Get user's permissions
        user_permissions = set()
        if user.is_superuser:
            # Superusers have all permissions
            user_permissions = set(cls.REQUIRED_PERMISSIONS)
        else:
            user_permissions = set(user.get_all_permissions())

        # Check required permissions
        required_set = set(cls.REQUIRED_PERMISSIONS)
        missing_permissions = required_set - user_permissions
        has_all_permissions = len(missing_permissions) == 0

        # Check for forbidden permissions (security check)
        forbidden_set = set(cls.FORBIDDEN_PERMISSIONS)
        forbidden_permissions_held = forbidden_set & user_permissions

        return {
            'is_cashier': is_cashier,
            'has_all_permissions': has_all_permissions,
            'missing_permissions': list(missing_permissions),
            'forbidden_permissions_held': list(forbidden_permissions_held),
            'total_permissions': len(user_permissions),
            'required_permissions_count': len(required_set),
            'error': None
        }

    @classmethod
    def setup_cashier_permissions(cls):
        """
        Set up all required permissions for the cashier group
        Returns success status and message
        """
        try:
            cashier_group = cls.get_cashier_group()

            # Clear existing permissions
            cashier_group.permissions.clear()

            assigned_count = 0
            errors = []

            for perm_string in cls.REQUIRED_PERMISSIONS:
                try:
                    app_label, codename = perm_string.split('.')
                    model_name = codename.split('_', 1)[1]  # Remove action prefix

                    content_type = ContentType.objects.get(
                        app_label=app_label,
                        model=model_name
                    )

                    permission = Permission.objects.get(
                        codename=codename,
                        content_type=content_type
                    )

                    cashier_group.permissions.add(permission)
                    assigned_count += 1

                except Exception as e:
                    error_msg = f"Permission not found: {perm_string} - {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)

                except ValueError as e:
                    error_msg = f"Invalid permission format: {perm_string} - {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            success = assigned_count > 0
            message = f"Assigned {assigned_count} permissions to Cashier group"

            if errors:
                message += f". {len(errors)} errors occurred."

            return {
                'success': success,
                'message': message,
                'assigned_count': assigned_count,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"Error setting up cashier permissions: {str(e)}")
            return {
                'success': False,
                'message': f"Error setting up permissions: {str(e)}",
                'assigned_count': 0,
                'errors': [str(e)]
            }

    @classmethod
    def add_user_to_cashier_group(cls, user):
        """Add a user to the cashier group"""
        try:
            cashier_group = cls.get_cashier_group()
            user.groups.add(cashier_group)
            return {
                'success': True,
                'message': f"User {user.username} added to Cashier group"
            }
        except Exception as e:
            logger.error(f"Error adding user to cashier group: {str(e)}")
            return {
                'success': False,
                'message': f"Error adding user to group: {str(e)}"
            }

    @classmethod
    def remove_user_from_cashier_group(cls, user):
        """Remove a user from the cashier group"""
        try:
            cashier_group = cls.get_cashier_group()
            user.groups.remove(cashier_group)
            return {
                'success': True,
                'message': f"User {user.username} removed from Cashier group"
            }
        except Exception as e:
            logger.error(f"Error removing user from cashier group: {str(e)}")
            return {
                'success': False,
                'message': f"Error removing user from group: {str(e)}"
            }

    @classmethod
    def get_cashier_users(cls):
        """Get all users in the cashier group"""
        cashier_group = cls.get_cashier_group()
        return User.objects.filter(groups=cashier_group)


def cashier_required(view_func):
    """
    Decorator to require cashier permissions for a view
    Usage: @cashier_required
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not CashierPermissions.is_cashier(request.user):
            logger.warning(f"Non-cashier user {request.user.username} attempted to access cashier view")
            raise PermissionDenied("Cashier access required")
        return view_func(request, *args, **kwargs)
    return wrapper


def cashier_permission_required(permission):
    """
    Decorator to require a specific permission for cashier views
    Usage: @cashier_permission_required('orders.change_order')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                logger.warning(f"User {request.user.username} lacks permission {permission}")
                raise PermissionDenied(f"Permission required: {permission}")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_cashier_access(user):
    """
    Quick function to check if user has cashier access
    Returns True/False
    """
    return CashierPermissions.is_cashier(user)


def get_cashier_permission_summary(user):
    """
    Get a formatted summary of cashier permissions for a user
    """
    status = CashierPermissions.check_cashier_permissions(user)

    summary = {
        'username': user.username,
        'is_authenticated': user.is_authenticated,
        'is_active': user.is_active,
        'is_cashier': status['is_cashier'],
        'has_all_permissions': status['has_all_permissions'],
        'permission_status': 'Complete' if status['has_all_permissions'] else 'Incomplete',
        'missing_count': len(status['missing_permissions']),
        'total_required': status['required_permissions_count'],
        'security_issues': len(status['forbidden_permissions_held']) > 0,
        'last_login': user.last_login,
        'groups': [group.name for group in user.groups.all()],
    }

    if status['missing_permissions']:
        summary['missing_permissions'] = status['missing_permissions']

    if status['forbidden_permissions_held']:
        summary['security_warning'] = f"User has {len(status['forbidden_permissions_held'])} forbidden permissions"
        summary['forbidden_permissions'] = status['forbidden_permissions_held']

    return summary
