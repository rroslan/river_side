# Admin Access Guide - River Side Food Court

## 🚀 Quick Start: Accessing Admin Features

### 1. **Main Admin Dashboard**
- **URL**: `http://localhost:8000/admin/`
- **Login**: Use your superuser credentials
- **What you'll see**:
  - Demo Data Management section with live stats
  - Orders, Vendors, Menu Items, Tables management
  - User and Group administration

### 2. **Demo Data Reset Options**

#### Option A: From Admin Dashboard
1. Go to `http://localhost:8000/admin/`
2. Look for the "🔄 Demo Data Management" section
3. Click "🗑️ Reset All Demo Data" button
4. Follow the confirmation prompts

#### Option B: Direct Reset Interface
1. Go to `http://localhost:8000/admin/data-reset/`
2. Review the warning message
3. Click "🗑️ Reset All Demo Data"
4. Watch real-time progress with live output

#### Option C: From Orders Admin
1. Go to `http://localhost:8000/admin/orders/order/`
2. Select any orders (or none - doesn't matter)
3. Choose "🔄 Reset All Demo Data" from Actions dropdown
4. Click "Go"

#### Option D: Command Line
```bash
cd river_side
python manage.py reset_demo_data --force
```

### 3. **Live Statistics API**
- **URL**: `http://localhost:8000/admin/api/stats/`
- **Method**: GET
- **Authentication**: Admin login required
- **Response**: JSON with current system stats

### 4. **What You'll See After Reset**
```
📊 Orders Today: 0
💰 Unpaid Orders: 0
🪑 Active Tables: 0
📦 Total Orders: 0
🪑 Available Tables: 25
```

### 5. **Creating Admin User (if needed)**
```bash
cd river_side
python manage.py createsuperuser
```

### 6. **Troubleshooting**

#### Can't see Demo Data Management section?
- Ensure you're logged in as staff/superuser
- Check that 'core' app is in INSTALLED_APPS
- Verify custom admin is loaded properly

#### Reset not working?
- Test command line first: `python manage.py reset_demo_data --force`
- Check Django logs for errors
- Verify database permissions

#### Permission denied?
- Ensure user has `is_staff=True`
- Check superuser status with `python manage.py shell`

### 7. **Security Notes**
- All reset methods require admin authentication
- Multiple confirmation steps prevent accidents
- All operations are logged
- CSRF protection enabled

### 8. **Quick Test**
```bash
# Test the management command
python manage.py reset_demo_data --force

# Check if admin URLs work
python manage.py check

# Verify admin access (creates test user)
python test_admin_integration.py
```

---
**🎯 Summary**: You now have 4 different ways to reset demo data, all accessible through the Django admin interface with proper authentication and safety measures.