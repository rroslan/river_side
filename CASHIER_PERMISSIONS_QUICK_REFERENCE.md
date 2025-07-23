# 🔐 Cashier Permissions - Quick Reference Guide

## 🚀 Quick Setup (Run These Commands)

```bash
# 1. Set up cashier permissions (REQUIRED FIRST)
python manage.py setup_cashier_permissions

# 2. Create a new cashier user
python manage.py add_cashier username --create --email "user@email.com" --first-name "First" --last-name "Last"

# 3. Or add existing user to cashier group
python manage.py add_cashier existing_username

# 4. Verify setup
python manage.py setup_cashier_permissions --list-users
```

## ✅ What Cashiers CAN Do

### Order Management
- ✅ View all orders
- ✅ Change order status (pending → confirmed → preparing → ready → delivered → paid)
- ✅ Mark orders as paid
- ✅ View order history and details
- ✅ Add status history notes

### Table Management
- ✅ View table information
- ✅ Reset tables (cancel pending orders)
- ✅ Change table status

### Payment Processing
- ✅ Process payments
- ✅ View payment history
- ✅ Generate payment receipts

### Reports & Information
- ✅ View sales reports
- ✅ Access vendor information
- ✅ View menu items and categories
- ✅ See customer information

### Cart Operations
- ✅ View and manage customer carts
- ✅ Modify cart items
- ✅ Delete carts when needed

## ❌ What Cashiers CANNOT Do

### User Management
- ❌ Create new users
- ❌ Delete users
- ❌ Modify user permissions
- ❌ Access user passwords

### Menu & Vendor Management
- ❌ Add/edit/delete menu items
- ❌ Change menu prices
- ❌ Create/delete vendors
- ❌ Modify vendor information

### System Administration
- ❌ Access Django admin for restricted models
- ❌ Modify system settings
- ❌ Create/delete orders (only modify status)
- ❌ Delete order items or order history

## 🛠️ Permission Management Commands

### Setup Commands
```bash
# Initial setup (creates group and assigns permissions)
python manage.py setup_cashier_permissions

# Reset permissions (clears and reassigns)
python manage.py setup_cashier_permissions --reset

# List all cashier users
python manage.py setup_cashier_permissions --list-users
```

### User Management Commands
```bash
# Create new cashier with prompts
python manage.py add_cashier new_username --create

# Create cashier with all details
python manage.py add_cashier john_doe --create \
    --email "john@restaurant.com" \
    --first-name "John" \
    --last-name "Doe" \
    --password "secure_password"

# Add existing user to cashier group
python manage.py add_cashier existing_user
```

## 🔍 Permission Verification

### Check User Permissions (Python Shell)
```python
from django.contrib.auth.models import User
from core.permissions import CashierPermissions

# Get user
user = User.objects.get(username='cashier_username')

# Check if user is a cashier
is_cashier = CashierPermissions.is_cashier(user)
print(f"Is cashier: {is_cashier}")

# Get detailed permission status
status = CashierPermissions.check_cashier_permissions(user)
print(f"Has all permissions: {status['has_all_permissions']}")
print(f"Missing permissions: {status['missing_permissions']}")

# Test specific permission
can_view_orders = user.has_perm('orders.view_order')
can_change_orders = user.has_perm('orders.change_order')
```

## 📋 Complete Permission List

### Orders App
- `orders.view_order` - View orders
- `orders.change_order` - Update order status, mark as paid
- `orders.view_orderitem` - View order items
- `orders.change_orderitem` - Modify order items
- `orders.view_orderstatushistory` - View status history
- `orders.add_orderstatushistory` - Add status history entries
- `orders.view_cart` - View customer carts
- `orders.change_cart` - Modify carts
- `orders.delete_cart` - Delete carts
- `orders.view_cartitem` - View cart items
- `orders.change_cartitem` - Modify cart items
- `orders.delete_cartitem` - Delete cart items

### Vendors App
- `vendors.view_vendor` - View vendor information
- `vendors.view_category` - View menu categories
- `vendors.view_menuitem` - View menu items
- `vendors.view_table` - View table information
- `vendors.change_table` - Reset tables, change status

### Auth App
- `auth.view_user` - View user information (limited)
- `auth.view_group` - View group information

## 🔒 Security Features

### Authentication
- Username/password required
- Session management
- Automatic logout on inactivity

### Authorization
- Group-based permissions
- Function-level permission checks
- Audit trail for all actions

### Audit Trail
- All order status changes logged
- Payment processing tracked
- Table reset actions recorded
- User activity monitoring

## 🚨 Troubleshooting

### Permission Issues
```bash
# User can't access cashier dashboard
python manage.py setup_cashier_permissions --list-users
# Check if user is in Cashier group

# User missing permissions
python manage.py setup_cashier_permissions --reset
# This will reassign all permissions

# Check specific user permissions
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='username')
>>> user.get_all_permissions()
```

### Common Problems
1. **"Permission denied" errors**: User not in Cashier group
2. **Can't mark orders as paid**: Missing `orders.change_order` permission
3. **Can't reset tables**: Missing `vendors.change_table` permission
4. **Dashboard won't load**: Run permission setup command

## 📞 Quick Support

### Command Check
```bash
# Verify Django is working
python manage.py check

# Check database
python manage.py showmigrations

# Test permissions
python manage.py setup_cashier_permissions --list-users
```

### Emergency Reset
```bash
# If permissions are completely broken
python manage.py setup_cashier_permissions --reset

# If user lost cashier access
python manage.py add_cashier username
```

---

## 🎯 Best Practices

1. **Always run setup first**: `python manage.py setup_cashier_permissions`
2. **Use management commands**: Don't manually assign permissions
3. **Regular verification**: Check permissions after updates
4. **Monitor access**: Review cashier user list regularly
5. **Security first**: Never give cashiers admin permissions
6. **Document changes**: Keep track of who has cashier access
7. **Test after setup**: Verify login and basic functions work

---

*For detailed information, see CASHIER.md*