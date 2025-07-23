# Visual Admin Navigation Guide

## 🎯 How to Access Demo Data Reset from Admin Dashboard

### Step 1: Start the Server
```bash
cd river_side
python manage.py runserver
```

### Step 2: Access Admin Dashboard
Open your browser and go to: `http://localhost:8000/admin/`

### Step 3: Login Screen
```
┌─────────────────────────────────────┐
│     Django Administration          │
├─────────────────────────────────────┤
│  Username: [your_username]          │
│  Password: [your_password]          │
│  [ Log in ]                         │
└─────────────────────────────────────┘
```

### Step 4: Main Admin Dashboard View
After login, you'll see:

```
┌─────────────────────────────────────────────────────────────┐
│  🏠 River Side Food Court Admin                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🔄 Demo Data Management                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📊 Orders Today: 5    💰 Unpaid Orders: 2         │   │
│  │  🪑 Active Tables: 3   📦 Total Orders: 45         │   │
│  │                                                     │   │
│  │  Reset all orders and return system to clean       │   │
│  │  demonstration state. Useful for preparing demos.  │   │
│  │                                                     │   │
│  │  [ 🗑️ Reset All Demo Data ]  [ 🔄 Refresh Stats ] │   │
│  │                                                     │   │
│  │  ⚠️ Warning: This will permanently delete all      │   │
│  │  orders and cannot be undone.                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📋 Administration                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ORDERS                                             │   │
│  │    🔸 Cart items    🔸 Carts                       │   │
│  │    🔸 Order items   🔸 Orders                      │   │
│  │    🔸 Order status histories                       │   │
│  │                                                     │   │
│  │  VENDORS                                            │   │
│  │    🔸 Categories    🔸 Menu items                  │   │
│  │    🔸 Tables        🔸 Vendors                     │   │
│  │                                                     │   │
│  │  AUTHENTICATION AND AUTHORIZATION                  │   │
│  │    🔸 Groups        🔸 Users                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 4 Ways to Reset Demo Data

### Method 1: From Dashboard (Above)
Click the `🗑️ Reset All Demo Data` button in the Demo Data Management section

### Method 2: Direct URL
Go to: `http://localhost:8000/admin/data-reset/`

You'll see:
```
┌─────────────────────────────────────────────────────────────┐
│  🔄 Reset Demo Data                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ⚠️ WARNING                                                 │
│  This action will permanently delete ALL orders and        │
│  reset the system to a clean state!                        │
│                                                             │
│  • All existing orders will be deleted                     │
│  • Order history will be lost                              │
│  • System will be reset to initial demonstration state     │
│  • This action cannot be undone                            │
│                                                             │
│  🎯 System ready for data reset                            │
│                                                             │
│  [ 🗑️ Reset All Demo Data ] [ ↩️ Cancel & Return to Admin ] │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ (Command output will appear here during reset)     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Method 3: From Orders Admin
1. Go to: `http://localhost:8000/admin/orders/order/`
2. You'll see:
```
┌─────────────────────────────────────────────────────────────┐
│  Select order to change                                     │
├─────────────────────────────────────────────────────────────┤
│  Action: [🔄 Reset All Demo Data    ▼]  [ Go ]             │
│                                                             │
│  ☑️ Order #12345  Table 5   $25.50  pending                │
│  ☑️ Order #12346  Table 3   $18.75  confirmed              │
│  ☑️ Order #12347  Table 1   $32.25  ready                  │
└─────────────────────────────────────────────────────────────┘
```

### Method 4: Command Line
```bash
cd river_side
python manage.py reset_demo_data --force
```

Output:
```
🚀 Starting River Side Food Court Data Reset
==================================================
🗑️  Clearing all data to reset state...
   Deleted 5 orders and related items
✅ System reset to clean state - all orders cleared
🧹 Ensuring clean state...
✅ System confirmed clean - no active orders

🔍 Verifying clean state...
📊 Orders Today: 0
💰 Unpaid Orders: 0
🪑 Active Tables: 0
📦 Total Orders: 0
🪑 Available Tables: 25

🎉 Data reset completed successfully!
```

## 📊 What Changes After Reset

### Before Reset:
```
📊 Orders Today: 15
💰 Unpaid Orders: 8
🪑 Active Tables: 6
📦 Total Orders: 150
```

### After Reset:
```
📊 Orders Today: 0
💰 Unpaid Orders: 0
🪑 Active Tables: 0
📦 Total Orders: 0
🪑 Available Tables: 25
```

## 🔧 Troubleshooting

### Problem: Can't see Demo Data Management section
**Solution**: Check that you're logged in as staff/superuser:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='your_username')
>>> print(f"Staff: {user.is_staff}, Superuser: {user.is_superuser}")
>>> # Should show: Staff: True, Superuser: True
```

### Problem: Reset button doesn't work
**Solution**: Test command line first:
```bash
python manage.py reset_demo_data --force
```

### Problem: Permission denied
**Solution**: Ensure you have admin access:
```bash
python manage.py createsuperuser
# Create new admin user if needed
```

## 🎯 Quick Test Checklist

- [ ] Can access `/admin/`
- [ ] Can see Demo Data Management section
- [ ] Stats show current numbers
- [ ] Reset button is visible
- [ ] Can access `/admin/data-reset/`
- [ ] Can run `python manage.py reset_demo_data --force`
- [ ] After reset, all stats show 0

## 📞 Need Help?

1. **Check Django logs**: Look in `logs/django.log`
2. **Run system check**: `python manage.py check`
3. **Test management command**: `python manage.py reset_demo_data --force`
4. **Verify admin setup**: `python test_admin_integration.py`

---

**🎉 Success!** You now have multiple ways to reset demo data directly from the Django admin interface!