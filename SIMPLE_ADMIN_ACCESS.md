# Simple Admin Access Guide - Demo Data Reset

## 🎯 Quick Access Methods

Since the Demo Data Management section might not be visible in your admin dashboard, here are **4 direct ways** to access the demo data reset functionality:

## Method 1: Direct URL Access ⭐ RECOMMENDED
```
http://localhost:8000/admin/data-reset/
```
- **Most reliable method**
- **Interactive interface with real-time progress**
- **Works independently of admin dashboard**
- **Full warning and confirmation system**

## Method 2: Command Line Access
```bash
cd river_side
python manage.py reset_demo_data --force
```
- **Always works**
- **Perfect for scripts and automation**
- **Immediate execution**

## Method 3: Orders Admin Action
1. Go to: `http://localhost:8000/admin/orders/order/`
2. Select any orders (selection doesn't matter)
3. Choose "🔄 Reset All Demo Data" from Actions dropdown
4. Click "Go"

## Method 4: Stats API
```bash
# Get current stats
curl http://localhost:8000/admin/api/stats/

# Reset via command line
python manage.py reset_demo_data --force
```

## 🚀 Step-by-Step Instructions

### Using Method 1 (Direct URL) - EASIEST:

1. **Start your server:**
   ```bash
   python manage.py runserver
   ```

2. **Open browser and go to:**
   ```
   http://localhost:8000/admin/data-reset/
   ```

3. **Login if prompted** (use your admin credentials)

4. **You'll see the reset interface:**
   ```
   🔄 Reset Demo Data
   
   ⚠️ WARNING
   This action will permanently delete ALL orders and reset 
   the system to a clean state!
   
   [🗑️ Reset All Demo Data] [↩️ Cancel & Return to Admin]
   ```

5. **Click "Reset All Demo Data"**

6. **Confirm in the popup dialog**

7. **Watch real-time progress**

### Using Method 2 (Command Line) - FASTEST:

```bash
cd river_side
python manage.py reset_demo_data --force
```

Output will show:
```
🚀 Starting River Side Food Court Data Reset
==================================================
🗑️  Clearing all data to reset state...
   Deleted X orders and related items
✅ System reset to clean state - all orders cleared
🎉 Data reset completed successfully!
```

## 🔍 Verification

After reset, check these URLs to verify:

1. **Stats API:**
   ```
   http://localhost:8000/admin/api/stats/
   ```
   Should return: `{"orders_today": 0, "unpaid_orders": 0, "active_tables": 0, "total_orders": 0}`

2. **Orders Admin:**
   ```
   http://localhost:8000/admin/orders/order/
   ```
   Should show: "0 orders"

3. **Command line check:**
   ```bash
   python manage.py reset_demo_data --force
   ```
   Should show all stats as 0

## 🎯 What Gets Reset

✅ **DELETED:**
- All orders and order items
- Order status history  
- Shopping cart data
- Order notifications

❌ **PRESERVED:**
- Vendors, categories, menu items
- User accounts and permissions
- Tables (ensures 25 tables available)
- System settings

## 📞 Troubleshooting

### Problem: "Permission denied"
**Solution:**
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='YOUR_USERNAME')
user.is_staff = True
user.is_superuser = True
user.save()
print('User permissions updated')
"
```

### Problem: "URL not found"
**Solution:**
1. Check server is running: `python manage.py runserver`
2. Verify URL: `http://localhost:8000/admin/data-reset/`
3. Try admin login first: `http://localhost:8000/admin/`

### Problem: "Template not found"
**Solution:**
Use command line method:
```bash
python manage.py reset_demo_data --force
```

### Problem: "Command not found"
**Solution:**
Ensure 'core' app is in INSTALLED_APPS:
```bash
python manage.py check
```

## 🎉 Success Indicators

After successful reset:
- 📊 Orders Today: 0
- 💰 Unpaid Orders: 0  
- 🪑 Active Tables: 0
- 📦 Total Orders: 0
- 🪑 Available Tables: 25

## 💡 Pro Tips

1. **Bookmark the direct URL:** `http://localhost:8000/admin/data-reset/`
2. **Use command line for scripts:** `python manage.py reset_demo_data --force`
3. **Check stats via API:** `curl http://localhost:8000/admin/api/stats/`
4. **Create test data first:** Run some orders, then reset to see the difference

## 🔗 Quick Links

- **Direct Reset Interface:** `/admin/data-reset/`
- **Stats API:** `/admin/api/stats/`  
- **Orders Admin:** `/admin/orders/order/`
- **Main Admin:** `/admin/`

---

**🎯 Bottom Line:** Use the direct URL method (`/admin/data-reset/`) for the best experience, or the command line method for quickest results. Both work independently of the main admin dashboard.