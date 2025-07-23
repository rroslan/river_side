# 🔐 Cashier Access Instructions

**River Side Food Court - Cashier System Access Guide**

---

## 🚪 How to Access the Cashier Dashboard

### Step 1: Open Cashier Login Page
Navigate to: **`http://localhost:8000/cashier/login/`**

### Step 2: Login with Cashier Credentials

#### Option A: Dedicated Cashier Account
- **Username:** `test_cashier`
- **Password:** `cashier123`
- **Email:** `cashier@test.com`

#### Option B: Admin Accounts (also have cashier access)
- **Username:** `admin` / `testadmin` / `rroslan`
- **Password:** [Your existing admin password]

### Step 3: Access Dashboard
After successful login, you'll be automatically redirected to:
**`http://localhost:8000/cashier/`**

---

## 🔧 Troubleshooting

### Problem: 403 Forbidden Error
**Cause:** Not logged in as a cashier user
**Solution:** Go to the login page first: `http://localhost:8000/cashier/login/`

### Problem: Invalid Login
**Cause:** Incorrect credentials or user not in cashier group
**Solution:** 
1. Verify username/password
2. Check if user has cashier permissions:
   ```bash
   python manage.py manage_cashier_users check [username]
   ```

### Problem: Missing Permissions
**Cause:** User not properly configured
**Solution:**
```bash
# Add user to cashier group
python manage.py manage_cashier_users add [username]

# Or reset all permissions
python manage.py setup_cashier_permissions --reset
```

---

## 👥 User Management

### Check Available Cashier Users
```bash
python manage.py manage_cashier_users list --detailed
```

### Create New Cashier User
```bash
python manage.py add_cashier [username] --create --email "[email]"
```

### Add Existing User to Cashier Group
```bash
python manage.py manage_cashier_users add [username]
```

---

## 🎯 Quick Access URLs

- **Cashier Login:** `http://localhost:8000/cashier/login/`
- **Cashier Dashboard:** `http://localhost:8000/cashier/`
- **Cashier Logout:** `http://localhost:8000/cashier/logout/`

---

## ✅ Success Indicators

After successful login, you should see:
- ✅ Cashier dashboard with order statistics
- ✅ List of orders ready for payment
- ✅ Table management options
- ✅ Sales reports access
- ✅ Payment processing buttons

---

## 🔒 Security Notes

- Only users in the "Cashier" group can access cashier functions
- Superusers (admins) automatically have cashier access
- All cashier actions are logged for audit purposes
- Sessions expire after inactivity for security

---

## 📞 Need Help?

1. **Check user permissions:** `python manage.py manage_cashier_users check [username]`
2. **Validate system:** `python validate_cashier_permissions.py`
3. **View all cashiers:** `python manage.py manage_cashier_users list`
4. **Reset permissions:** `python manage.py setup_cashier_permissions --reset`

For detailed documentation, see: `CASHIER.md`
