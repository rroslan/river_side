# River Side Food Court - Cashier System Guide

## 🎯 Quick Start

**Need to access the cashier system right now?**

1. **Go to**: `http://localhost:8000/cashier/`
2. **Login with default credentials**:
   - Username: `cashier`
   - Password: `cashier123`
3. **Start processing payments!**

---

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Creating Cashier Staff](#creating-cashier-staff)
- [Accessing Cashier Dashboard](#accessing-cashier-dashboard)
- [Dashboard Features](#dashboard-features)
- [Payment Processing](#payment-processing)
- [Table Management](#table-management)
- [Reports & Analytics](#reports--analytics)
- [Permissions & Security](#permissions--security)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

---

## 🏪 System Overview

The River Side Food Court cashier system provides a comprehensive point-of-sale (POS) interface for processing payments, managing tables, and tracking sales. It's designed specifically for food court operations where multiple vendors serve customers at shared tables.

### Key Features
- **Payment Processing**: Mark orders as paid with multiple payment methods
- **Real-time Dashboard**: Live statistics and order monitoring
- **Table Management**: Reset tables and manage customer flow
- **Multi-vendor Support**: Track sales across all food court vendors
- **Sales Reports**: Daily revenue tracking and analytics
- **Order Tracking**: Complete order lifecycle management

### User Types
- **Cashiers**: Process payments and manage tables
- **Staff**: Full access including admin functions
- **Superusers**: Complete system administration

---

## 👥 Creating Cashier Staff

### Method 1: Using Management Command (Recommended)

**Create a basic cashier:**
```bash
cd river_side
python manage.py create_cashier john_doe
```

**Create cashier with custom settings:**
```bash
# Basic cashier (staff access, no admin)
python manage.py create_cashier sarah --email sarah@restaurant.com --password secure123

# Cashier with admin access
python manage.py create_cashier manager --email manager@restaurant.com --staff --password admin123

# Cashier with full superuser access
python manage.py create_cashier admin_cashier --email admin@restaurant.com --superuser --password super123
```

**Command Options:**
- `username` (required): Cashier username
- `--email`: Email address (default: username@restaurant.com)
- `--password`: Password (default: cashier123)
- `--staff`: Grant staff access (admin panel access)
- `--superuser`: Grant superuser access (full admin)

### Method 2: Using Django Admin

1. **Access Admin Panel**: `http://localhost:8000/admin/`
2. **Go to Users**: Click "Users" under Authentication
3. **Add User**: Click "Add User" button
4. **Fill Details**:
   - Username: `cashier_name`
   - Password: `secure_password`
5. **Set Permissions**:
   - ✅ Active
   - ✅ Staff status (for admin access)
   - Add to "Cashiers" group
6. **Save User**

### Method 3: Programmatic Creation

```python
# Django shell: python manage.py shell
from django.contrib.auth.models import User, Group

# Create user
user = User.objects.create_user(
    username='new_cashier',
    email='cashier@restaurant.com',
    password='secure123',
    is_staff=True  # For admin access
)

# Add to Cashiers group
cashiers_group, created = Group.objects.get_or_create(name='Cashiers')
user.groups.add(cashiers_group)
```

### Default Credentials

For testing and initial setup, default credentials are available:

```
Username: cashier
Password: cashier123
Access Level: Staff + Cashiers group
```

**⚠️ Security Note**: Change default passwords in production!

---

## 🚪 Accessing Cashier Dashboard

### Login Process

1. **Navigate to Cashier Login**:
   ```
   http://localhost:8000/cashier/login/
   ```

2. **Enter Credentials**:
   - Username: Your cashier username
   - Password: Your assigned password

3. **Dashboard Access**:
   - Upon successful login, you'll be redirected to the main dashboard
   - Direct URL: `http://localhost:8000/cashier/`

### Navigation Structure

```
🏠 Main Dashboard (/cashier/)
├── 📊 Order Processing
├── 🪑 Table Management  
├── 📈 Sales Reports
├── ⚙️ Admin Panel (if staff)
└── 🚪 Logout
```

### Quick Access Links

From any page in the restaurant system:
- **Table Selection Page**: Look for "Admin Panel" link at bottom
- **Any Order Page**: Links to cashier dashboard in navigation
- **Direct URL**: Always available at `/cashier/`

---

## 📊 Dashboard Features

### Statistics Overview

The dashboard displays real-time statistics:

```
📋 Orders Today: 45        💰 Revenue Today: $1,250.75
🔄 Unpaid Orders: 12       ✅ Paid Today: 33
🪑 Active Tables: 8        📊 Table Capacity: 25
```

**Metrics Explained:**
- **Orders Today**: Total orders created today
- **Unpaid Orders**: Orders ready for payment (status: delivered/ready)
- **Paid Today**: Orders marked as paid today
- **Revenue Today**: Total cash collected today
- **Active Tables**: Tables with pending/active orders

### Live Order Display

Orders are displayed in a filterable list showing:
- **Order ID**: Unique identifier (first 8 characters)
- **Table Number**: Customer location
- **Customer Info**: Name and phone
- **Status**: Current order status
- **Total Amount**: Payment due
- **Timestamp**: When order was created
- **Actions**: Payment and management buttons

### Filter Options

**Status Filters:**
- `All Orders`: Show all orders
- `Unpaid`: Orders ready for payment (delivered/ready)
- `Paid`: Completed transactions
- `Pending`: Orders still being prepared

**Table Filters:**
- `All Tables`: Show orders from all tables
- `Table 1-25`: Filter by specific table number

**Date Filters:**
- `Today`: Orders from today only
- `Yesterday`: Previous day orders
- `This Week`: Last 7 days
- `All Time`: No date restriction

---

## 💳 Payment Processing

### Basic Payment Flow

1. **Locate Order**: Find the order in the dashboard list
2. **Verify Details**: Check order contents and total
3. **Process Payment**: Click "Mark as Paid" button
4. **Confirm Payment**: Select payment method and confirm
5. **Order Complete**: Order status changes to "Paid"

### Payment Methods

The system supports multiple payment methods:

- **💵 Cash**: Traditional cash payment
- **💳 Card**: Credit/debit card transactions
- **📱 Digital**: Mobile payments (Apple Pay, Google Pay, etc.)
- **🏧 Bank Transfer**: Direct bank transfers
- **🎁 Voucher**: Gift cards or vouchers
- **🆓 Comp**: Complimentary (free) items

### Step-by-Step Payment Process

#### Step 1: Select Order
```
📋 Order #abc123ef - Table 5
👤 Customer: John Smith
📞 Phone: +1234567890
💰 Total: $24.75
🕐 Created: 2:30 PM
```

#### Step 2: Click "Mark as Paid"
- Button appears for orders with status "delivered" or "ready"
- Opens payment confirmation dialog

#### Step 3: Payment Dialog
```
💳 Process Payment - Order #abc123ef

Payment Amount: $24.75
Payment Method: [Cash ▼]
Notes (optional): [________________]

[Cancel] [Confirm Payment]
```

#### Step 4: Payment Confirmation
```
✅ Payment Successful!

Order: #abc123ef
Amount: $24.75
Method: Cash
Time: 2:45 PM
Status: Paid
```

### Payment Validation

The system automatically validates:
- **Amount Check**: Payment amount must equal or exceed order total
- **Status Check**: Only delivered/ready orders can be marked paid
- **Duplicate Prevention**: Prevents double-payment of same order

### Payment Notes

Add optional notes for:
- **Change Given**: "Paid $30, change $5.25"
- **Card Details**: "Visa ending in 1234"
- **Special Instructions**: "Customer requested receipt via email"

---

## 🪑 Table Management

### Table Status Overview

Access via "Tables" button in navigation:

```
🪑 Table Status Overview

Table 1: 🟢 Available    Table 14: 🔴 Occupied (2 orders)
Table 2: 🟡 Ordering     Table 15: 🟢 Available
Table 3: 🔴 Occupied     Table 16: 🟡 Ordering
...
```

**Status Indicators:**
- 🟢 **Available**: No active orders, ready for customers
- 🟡 **Ordering**: Customer browsing menu or placing order
- 🔴 **Occupied**: Has unpaid orders, customers at table
- ⚫ **Inactive**: Table disabled in system

### Reset Table Function

When customers leave without paying or tables need clearing:

#### Step 1: Identify Problem Table
```
Table 12: 🔴 Occupied
- Order #def456gh: $18.50 (delivered 30 min ago)
- Order #ghi789jk: $12.25 (ready)
```

#### Step 2: Reset Process
1. Click "Reset Table" button
2. Select cancellation reason:
   - Customer left without paying
   - Orders were cancelled
   - System error correction
   - Other (specify)
3. Confirm table reset

#### Step 3: Result
```
✅ Table 12 Reset Successfully

Actions Taken:
- Cancelled 2 orders
- Total amount: $30.75
- Status: Available
- Ready for new customers
```

### Table Reset Considerations

**When to Reset:**
- ✅ Customer left without paying
- ✅ Orders were cancelled by kitchen
- ✅ System error needs correction
- ✅ Table needs immediate availability

**When NOT to Reset:**
- ❌ Customer stepped away temporarily
- ❌ Orders are still being prepared
- ❌ Payment is expected soon
- ❌ Customer disputes exist

---

## 📈 Reports & Analytics

### Daily Sales Report

Access via "Sales" button in navigation:

```
📊 Daily Sales Report - [Current Date]

💰 REVENUE SUMMARY
├── Total Revenue: $2,450.75
├── Cash Payments: $1,200.50 (49%)
├── Card Payments: $1,100.25 (45%)
└── Other Methods: $150.00 (6%)

📋 ORDER SUMMARY  
├── Total Orders: 98
├── Paid Orders: 85 (87%)
├── Unpaid Orders: 8 (8%)
└── Cancelled Orders: 5 (5%)

🏪 VENDOR BREAKDOWN
├── Pizza Corner: $980.25 (40%)
├── Asian Delights: $875.50 (36%)
└── Fresh Juice Bar: $595.00 (24%)
```

### Vendor Performance Tracking

```
🏪 Vendor Analysis

Pizza Corner
├── Orders: 35 (36% of total)
├── Revenue: $980.25 (40% of total)
├── Avg Order: $28.01
├── Paid: $845.75 | Unpaid: $134.50

Asian Delights  
├── Orders: 28 (29% of total)
├── Revenue: $875.50 (36% of total)
├── Avg Order: $31.27
├── Paid: $800.00 | Unpaid: $75.50

Fresh Juice Bar
├── Orders: 35 (36% of total) 
├── Revenue: $595.00 (24% of total)
├── Avg Order: $17.00
├── Paid: $560.00 | Unpaid: $35.00
```

### Export Options

Reports can be exported in multiple formats:
- **📊 CSV**: For spreadsheet analysis
- **📄 PDF**: For printing and records
- **📧 Email**: Direct delivery to management
- **📋 Print**: Immediate hard copy

---

## 🔐 Permissions & Security

### User Access Levels

#### Level 1: Cashier (Basic)
```
✅ Permissions:
- Access cashier dashboard
- View orders and statistics
- Process payments
- Reset tables
- View sales reports

❌ Restrictions:
- No admin panel access
- Cannot modify menu items
- Cannot create users
- Cannot access system settings
```

#### Level 2: Staff Cashier
```
✅ Additional Permissions:
- Admin panel access
- Modify order details
- View all admin reports
- Manage table settings
- Access user management

❌ Restrictions:
- Cannot create superusers
- Limited system configuration
```

#### Level 3: Superuser Cashier
```
✅ Full Permissions:
- Complete admin access
- Create/modify users
- System configuration
- Database management
- All cashier functions
```

### Security Features

**Authentication:**
- Username/password login required
- Session timeout after inactivity
- Secure password requirements

**Authorization:**
- Group-based permissions (Cashiers group)
- Role-based access control
- Function-level permission checks

**Audit Trail:**
- All payment actions logged
- User activity tracking
- Order modification history
- Table reset records

**Data Protection:**
- CSRF protection on all forms
- SQL injection prevention
- XSS protection
- Secure session management

## 🔧 Setting Up Cashier Permissions

### Initial Setup (Required)

Before creating any cashier users, you MUST set up the proper permissions:

```bash
# Navigate to your project directory
cd river_side

# Set up cashier group and permissions
python manage.py setup_cashier_permissions
```

This command will:
- Create the "Cashier" group if it doesn't exist
- Assign all required permissions
- Verify permissions are correctly set
- Show a summary of what cashiers can do

### Creating New Cashier Users

#### Method 1: Create User and Add to Group (Recommended)
```bash
# Create new user with all details
python manage.py add_cashier john_doe --create \
    --email "john@restaurant.com" \
    --first-name "John" \
    --last-name "Doe"

# You'll be prompted for password
```

#### Method 2: Add Existing User to Cashier Group
```bash
# Add existing user to cashier group
python manage.py add_cashier existing_username
```

### Permission Verification

Check if permissions are properly set:

```bash
# List all cashier users and their status
python manage.py setup_cashier_permissions --list-users

# Reset permissions if needed
python manage.py setup_cashier_permissions --reset
```

### Programmatic Permission Check

You can also check permissions programmatically:

```python
from core.permissions import CashierPermissions

# Check if user is a cashier
user = User.objects.get(username='cashier_username')
is_cashier = CashierPermissions.is_cashier(user)

# Get detailed permission status
status = CashierPermissions.check_cashier_permissions(user)
print(f"Has all permissions: {status['has_all_permissions']}")
print(f"Missing permissions: {status['missing_permissions']}")

# Add user to cashier group
result = CashierPermissions.add_user_to_cashier_group(user)
print(result['message'])
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: Cannot Access Cashier Dashboard

**Symptoms:**
- "Permission denied" error
- Redirected to login page
- "You do not have permission" message

**Solutions:**
```bash
# Check user permissions
python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='YOUR_USERNAME')
print(f'Staff: {user.is_staff}')
print(f'Groups: {[g.name for g in user.groups.all()]}')
"

# Fix permissions
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.get(username='YOUR_USERNAME')
cashiers_group, created = Group.objects.get_or_create(name='Cashiers')
user.groups.add(cashiers_group)
user.is_staff = True
user.save()
print('Permissions updated')
"
```

#### Issue 2: Orders Not Appearing

**Symptoms:**
- Dashboard shows no orders
- Known orders missing from list
- Statistics show zero

**Solutions:**
```bash
# Check database connection
python manage.py shell -c "
from orders.models import Order
print(f'Total orders in database: {Order.objects.count()}')
print(f'Unpaid orders: {Order.objects.filter(status__in=[\"delivered\", \"ready\"]).count()}')
"

# Clear cache if needed
python manage.py shell -c "
from django.core.cache import cache
cache.clear()
print('Cache cleared')
"
```

#### Issue 3: Payment Processing Fails

**Symptoms:**
- "Mark as Paid" button doesn't work
- JavaScript errors in browser
- Payment doesn't save

**Solutions:**
1. **Check Browser Console**: Press F12, look for JavaScript errors
2. **Verify CSRF Token**: Ensure forms have proper CSRF protection
3. **Test with Different Browser**: Rule out browser-specific issues
4. **Check Network**: Ensure stable internet connection

```bash
# Test payment API directly
curl -X POST http://localhost:8000/cashier/mark-paid/ORDER_ID/ \
  -H "Content-Type: application/json" \
  -d '{"payment_method": "cash", "payment_amount": 25.50}'
```

#### Issue 4: Table Reset Not Working

**Symptoms:**
- Table stays occupied after reset
- Orders not cancelled properly
- Reset button missing

**Solutions:**
```bash
# Check table status
python manage.py shell -c "
from vendors.models import Table
from orders.models import Order
table = Table.objects.get(number=TABLE_NUMBER)
orders = Order.objects.filter(
    table=table,
    status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
)
print(f'Active orders for table {table.number}: {orders.count()}')
for order in orders:
    print(f'  Order {order.id}: {order.status}')
"

# Manually reset table
python manage.py shell -c "
from vendors.models import Table
from orders.models import Order, OrderStatus
table = Table.objects.get(number=TABLE_NUMBER)
orders = Order.objects.filter(
    table=table,
    status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
)
for order in orders:
    order.status = OrderStatus.CANCELLED
    order.save()
print(f'Reset {orders.count()} orders for table {table.number}')
"
```

### Getting Help

1. **Check Django Logs**: `logs/django.log`
2. **Run System Check**: `python manage.py check`
3. **Test Basic Functions**: Login, view orders, process test payment
4. **Contact System Administrator**: Provide error messages and steps to reproduce

---

## 🔌 API Reference

### Authentication

All API endpoints require authentication. Include session cookies or use token authentication.

### Endpoints

#### Mark Order as Paid
```http
POST /cashier/mark-paid/{order_id}/
Content-Type: application/json

{
    "payment_method": "cash|card|digital|bank_transfer|voucher|comp",
    "payment_amount": 25.50,
    "notes": "Optional payment notes"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Order marked as paid via cash",
    "order_id": "abc123ef-1234-5678-9012-def456789abc",
    "old_status": "delivered",
    "new_status": "paid",
    "paid_at": "2024-01-15T14:30:00Z",
    "total_amount": "25.50"
}
```

#### Reset Table
```http
POST /cashier/reset-table/{table_number}/
Content-Type: application/json

{
    "reason": "Customer left without paying"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Table 5 has been reset",
    "orders_cancelled": 2,
    "cancelled_orders": [
        {"id": "abc123ef", "old_status": "delivered", "total_amount": "18.50"},
        {"id": "def456gh", "old_status": "ready", "total_amount": "12.25"}
    ],
    "table_number": 5
}
```

#### Get Order Details
```http
GET /cashier/order/{order_id}/
```

**Response:**
```json
{
    "id": "abc123ef-1234-5678-9012-def456789abc",
    "table": 5,
    "customer_name": "John Smith",
    "customer_phone": "+1234567890",
    "status": "delivered",
    "total_amount": "25.50",
    "created_at": "2024-01-15T14:00:00Z",
    "items": [
        {
            "menu_item": "Margherita Pizza",
            "quantity": 1,
            "unit_price": "18.50",
            "subtotal": "18.50"
        },
        {
            "menu_item": "Coca Cola",
            "quantity": 2,
            "unit_price": "3.50",
            "subtotal": "7.00"
        }
    ]
}
```

---

## 🎯 Best Practices

### Daily Operations

**Opening Checklist:**
- [ ] Login to cashier dashboard
- [ ] Verify all tables show as available
- [ ] Check yesterday's unpaid orders
- [ ] Review overnight system changes
- [ ] Test payment processing

**During Service:**
- [ ] Monitor unpaid orders regularly
- [ ] Process payments promptly
- [ ] Reset tables when customers leave
- [ ] Track cash vs card payments
- [ ] Assist customers with payment questions

**Closing Checklist:**
- [ ] Process all outstanding payments
- [ ] Generate daily sales report
- [ ] Reset any abandoned tables
- [ ] Log any issues or discrepancies
- [ ] Secure cash drawer

### Payment Processing

**Best Practices:**
- ✅ Verify order contents before payment
- ✅ Confirm payment amount matches total
- ✅ Select correct payment method
- ✅ Add notes for cash transactions (change given)
- ✅ Provide receipt if requested

**Avoid:**
- ❌ Processing payments for wrong orders
- ❌ Accepting payments below order total
- ❌ Forgetting to mark orders as paid
- ❌ Processing duplicate payments

### Customer Service

**Professional Standards:**
- Greet customers warmly
- Verify order details clearly
- Process payments efficiently
- Handle disputes calmly
- Maintain clean workspace

**Communication:**
- "Your order total is $25.50"
- "Will that be cash or card today?"
- "Your change is $4.50"
- "Thank you for visiting River Side!"

---

## 📞 Support & Resources

### Quick Reference

- **Cashier Login**: `http://localhost:8000/cashier/login/`
- **Main Dashboard**: `http://localhost:8000/cashier/`
- **Admin Panel**: `http://localhost:8000/admin/`
- **Table Overview**: `http://localhost:8000/cashier/tables-overview/`
- **Sales Report**: `http://localhost:8000/cashier/sales-report/`

### Documentation Files

- `CASHIER.md` - This complete guide (you are here)
- `RESET.md` - Demo data reset functionality
- `ADMIN_DEMO_RESET.md` - Admin system features
- `README.md` - General system overview

### Command Reference

#### Core Permission Setup
```bash
# Set up cashier permissions (REQUIRED - run this first)
python manage.py setup_cashier_permissions

# Reset permissions if issues occur
python manage.py setup_cashier_permissions --reset

# List all cashier users and their status
python manage.py setup_cashier_permissions --list-users
```

#### User Management Commands
```bash
# Create new cashier user with prompts
python manage.py add_cashier username --create

# Create cashier with all details at once
python manage.py add_cashier john_doe --create \
    --email "john@restaurant.com" \
    --first-name "John" \
    --last-name "Doe"

# Add existing user to cashier group
python manage.py add_cashier existing_username
```

#### Advanced User Management
```bash
# List all cashier users
python manage.py manage_cashier_users list

# List with detailed permission info
python manage.py manage_cashier_users list --detailed

# Add user to cashier group
python manage.py manage_cashier_users add username

# Remove user from cashier group
python manage.py manage_cashier_users remove username

# Check specific user permissions
python manage.py manage_cashier_users check username

# Audit all cashier users for issues
python manage.py manage_cashier_users audit

# Audit and automatically fix issues
python manage.py manage_cashier_users audit --fix-issues

# Backup cashier user list
python manage.py manage_cashier_users backup

# Restore from backup
python manage.py manage_cashier_users restore cashier_backup.txt
```

#### System Maintenance
```bash
# Validate entire permissions system
python validate_cashier_permissions.py

# Reset demo data (testing)
python manage.py reset_demo_data --force

# Check system status
python manage.py check

# Access Django shell
python manage.py shell
```

### Training Resources

**New Cashier Training:**
1. Read this documentation thoroughly
2. Practice with demo data
3. Test all payment methods
4. Learn table management
5. Review security procedures

**Advanced Training:**
- Admin panel navigation
- Report generation
- User management
- System configuration
- Troubleshooting procedures

---

## 🎉 Success Checklist

After reading this guide, you should be able to:

### Initial Setup
- [ ] Set up cashier permissions: `python manage.py setup_cashier_permissions`
- [ ] Create new cashier users: `python manage.py add_cashier username --create`
- [ ] Verify permissions are working: `python validate_cashier_permissions.py`
- [ ] Test login and dashboard access

### Daily Operations
- [ ] Access the cashier dashboard at `/cashier/`
- [ ] Process customer payments and mark orders as paid
- [ ] Reset tables when needed using the reset function
- [ ] Generate and review sales reports
- [ ] Handle common troubleshooting issues
- [ ] Use filter options to find specific orders

### User Management
- [ ] List all cashier users: `python manage.py manage_cashier_users list`
- [ ] Add new users to cashier group: `python manage.py manage_cashier_users add username`
- [ ] Remove users when needed: `python manage.py manage_cashier_users remove username`
- [ ] Check individual user permissions: `python manage.py manage_cashier_users check username`
- [ ] Audit all users regularly: `python manage.py manage_cashier_users audit`

### System Administration
- [ ] Understand permission levels and security model
- [ ] Use management commands effectively for maintenance
- [ ] Troubleshoot permission issues using built-in tools
- [ ] Monitor cashier activity through audit logs
- [ ] Backup and restore user configurations
- [ ] Validate system integrity regularly

### Security & Compliance
- [ ] Understand what cashiers can and cannot do
- [ ] Know how to check user permissions programmatically
- [ ] Follow proper security procedures for user management
- [ ] Maintain audit trail compliance for all transactions
- [ ] Monitor for unauthorized access attempts
- [ ] Keep permissions up to date with system changes

### Best Practices
- [ ] Train new cashiers on system procedures
- [ ] Document any custom workflows or policies
- [ ] Regular permission audits and cleanup
- [ ] Test backup and restore procedures
- [ ] Keep management commands reference handy
- [ ] Monitor system performance and user feedback

**🎯 You're now ready to efficiently manage the River Side Food Court cashier system!**

---

*River Side Food Court - Cashier System v1.0*  
*Last Updated: 2024*  
*Status: Production Ready ✅*