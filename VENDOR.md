# 🏪 Vendor Dashboard Guide
## River Side Food Court Management System

### 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Logging In](#logging-in)
3. [Dashboard Overview](#dashboard-overview)
4. [Menu Management](#menu-management)
5. [Order Management](#order-management)
6. [Payment Tracking](#payment-tracking)
7. [Analytics & Reports](#analytics--reports)
8. [Troubleshooting](#troubleshooting)
9. [Contact Support](#contact-support)

---

## 🚀 Getting Started

Welcome to the River Side Food Court vendor management system! This guide will help you navigate your vendor dashboard and manage your business operations effectively.

### 🔐 Logging In

**Method 1: Admin Panel Login (Primary)**
1. Go to: `https://yoursite.com/admin/`
2. Enter your vendor credentials:
   - **Username**: Your assigned vendor username
   - **Password**: Your assigned password
3. After login, navigate to: `https://yoursite.com/vendors/`

**Method 2: Direct Dashboard Access**
1. If already logged in, visit: `https://yoursite.com/vendors/`
2. Click on your vendor card to access the dashboard

### 👤 Default Vendor Accounts
- **Drinks Vendor**: `drink_vendor`
- **Asian Food**: `asian_vendor` 
- **Pizza Corner**: `pizza_vendor`

> 💡 **Note**: Contact the administrator if you need password reset or new account creation.

---

## 📊 Dashboard Overview

### 🏠 Main Dashboard (`/vendors/<id>/dashboard/`)

Your dashboard provides real-time insights into your business:

#### 📈 Key Statistics
- **Pending Orders**: Orders waiting for confirmation
- **Preparing Orders**: Orders currently being prepared
- **Ready Orders**: Orders ready for pickup/delivery
- **Today's Revenue**: Daily earnings from paid orders
- **Unpaid Revenue**: Revenue from delivered orders awaiting payment

#### 🔄 Real-Time Order Feed
- Live updates of incoming orders
- Order details including:
  - Table number
  - Customer name
  - Items ordered
  - Special instructions
  - Order total

#### 💰 Payment Status
- **Paid Orders**: Completed transactions
- **Unpaid Orders**: Delivered orders awaiting payment
- Revenue breakdown by payment method

---

## 🍽️ Menu Management

### 📝 Accessing Menu Management
1. From vendor dashboard, click **"Manage Menu"**
2. Or visit: `/vendors/<id>/menu/`

### ✅ What You Can Do

#### Toggle Item Availability
- **Enable/Disable** menu items in real-time
- Items marked "unavailable" won't appear to customers
- Perfect for handling ingredient shortages or daily specials

#### View Menu Organization
- Browse items by **category**
- See item details:
  - Name, description, price
  - Preparation time
  - Dietary information (vegetarian, vegan, spicy)
  - Current availability status

### ❌ What Requires Admin Access

#### Adding New Items
- **Location**: `/admin/vendors/menuitem/add/`
- **Required**: Staff access or contact administrator
- **Include**: Name, description, price, category, image

#### Editing Item Details
- **Location**: `/admin/vendors/menuitem/<id>/change/`
- **Editable**: Price, description, images, dietary info
- **Required**: Staff access

#### Managing Categories
- **Location**: `/admin/vendors/category/`
- **Actions**: Create, edit, reorder categories
- **Required**: Staff access

#### Updating Vendor Info & Logo
- **Location**: `/admin/vendors/vendor/<id>/change/`
- **Editable**: Logo, description, hours, contact info
- **Required**: Staff access

---

## 📦 Order Management

### 🔄 Order Status Workflow
1. **Pending** → Customer placed order
2. **Confirmed** → You accepted the order
3. **Preparing** → Order is being prepared
4. **Ready** → Order ready for pickup/delivery
5. **Delivered** → Order given to customer
6. **Paid** → Payment completed

### ⚡ Updating Order Status

#### From Dashboard
1. Find the order in your order feed
2. Click on the order status dropdown
3. Select new status
4. Status updates instantly across the system

#### Status Change Options
- **Pending → Confirmed**: Accept the order
- **Confirmed → Preparing**: Start cooking
- **Preparing → Ready**: Order complete
- **Ready → Delivered**: Given to customer (done by cashier)

### 📱 Kitchen Display
- Access: `/vendors/kitchen/`
- Shows all active orders across vendors
- Organized by vendor for easy viewing
- Real-time updates

---

## 💳 Payment Tracking

### 📊 Revenue Analytics

#### Daily Summary
- **Today's Revenue**: Total paid orders for today
- **Unpaid Revenue**: Orders delivered but not yet paid
- **Order Count**: Number of orders processed

#### Payment Methods
- **Cash**: Physical cash payments
- **Card**: Credit/debit card transactions  
- **Mobile**: Mobile payment apps
- **Other**: Alternative payment methods

### 📈 Payment Reports

#### Accessing Reports
1. From dashboard, scroll to **"Payment Analytics"**
2. Or use API endpoint: `/vendors/<id>/api/payment-report/`

#### Report Data Includes
- **Date Range**: Customizable reporting period
- **Revenue Breakdown**: Paid vs unpaid amounts
- **Top Selling Items**: Best performers by revenue
- **Daily Trends**: Revenue patterns over time
- **Order Details**: Individual transaction records

---

## 📊 Analytics & Reports

### 🎯 Key Metrics to Monitor

#### Order Volume
- **Peak Hours**: Identify busy periods
- **Daily Patterns**: Understand customer behavior
- **Item Popularity**: Track best-selling items

#### Revenue Performance
- **Daily Revenue**: Track daily earnings
- **Average Order Value**: Monitor customer spending
- **Payment Completion Rate**: Track unpaid orders

#### Operational Efficiency
- **Preparation Times**: Monitor kitchen performance
- **Order Accuracy**: Track order completion
- **Customer Satisfaction**: Monitor feedback

### 📱 Real-Time Monitoring

#### Live Dashboard Features
- **Auto-refresh**: Updates every 30 seconds
- **WebSocket Integration**: Instant order notifications
- **Status Indicators**: Visual order status tracking

---

## 🛠️ Troubleshooting

### 🔒 Login Issues

**Problem**: Can't access dashboard
**Solutions**:
1. Verify username/password with administrator
2. Clear browser cache and cookies
3. Try incognito/private browser mode
4. Contact admin for password reset

### 🍽️ Menu Issues

**Problem**: Items not appearing for customers
**Check**:
1. Item availability toggle is **ON**
2. Category is active
3. Vendor is marked as active
4. Item has valid price and description

**Problem**: Can't update item details
**Solution**: Use admin panel or contact administrator

### 📦 Order Issues

**Problem**: Orders not updating
**Solutions**:
1. Refresh the page
2. Check internet connection
3. Verify order status in admin panel
4. Contact technical support

### 💰 Payment Issues

**Problem**: Revenue not matching expectations
**Check**:
1. Filter date ranges correctly
2. Include both paid and unpaid orders
3. Verify payment method categorization
4. Contact cashier for payment confirmation

---

## 📞 Contact Support

### 🏢 Administrative Support
- **Account Issues**: Contact system administrator
- **Menu Setup**: Request category/item creation
- **Logo Updates**: Request vendor info changes
- **Technical Issues**: Report system problems

### 💡 Feature Requests
- **New Functionality**: Suggest dashboard improvements
- **Integration Needs**: Request third-party connections
- **Reporting Requirements**: Request custom reports

### 🚨 Emergency Support
- **Payment Issues**: Immediate cashier assistance
- **System Downtime**: Technical emergency support
- **Order Problems**: Real-time order management help

---

## 📚 Quick Reference

### 🔗 Important URLs
- **Vendor List**: `/vendors/`
- **Dashboard**: `/vendors/<id>/dashboard/`
- **Menu Management**: `/vendors/<id>/menu/`
- **Kitchen Display**: `/vendors/kitchen/`
- **Admin Panel**: `/admin/`

### ⌨️ Keyboard Shortcuts
- **Refresh Dashboard**: `F5` or `Ctrl+R`
- **New Tab**: `Ctrl+T`
- **Switch Tabs**: `Ctrl+Tab`

### 📱 Mobile Access
- **Responsive Design**: Works on tablets and phones
- **Touch-Friendly**: Optimized for touch interfaces
- **Offline Capability**: Basic functionality when offline

---

## 🔄 Best Practices

### 🕐 Daily Operations
1. **Check dashboard** at start of business day
2. **Update item availability** based on inventory
3. **Monitor orders** throughout the day
4. **Review revenue** at end of day

### 📊 Weekly Review
1. **Analyze top-selling items**
2. **Review payment completion rates**
3. **Check operational efficiency metrics**
4. **Plan menu updates or specials**

### 🎯 Optimization Tips
1. **Toggle unavailable items** to improve customer experience
2. **Monitor preparation times** to set realistic expectations
3. **Track payment delays** and coordinate with cashier
4. **Use analytics** to identify growth opportunities

---

*Last Updated: January 2024*
*Version: 1.0*

> 💡 **Need Help?** Contact your system administrator or refer to this guide for step-by-step instructions.