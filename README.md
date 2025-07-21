# 🏞️ River Side Food Court

A modern, real-time food court management system built with Django, Channels, WebSockets, and Alpine.js. Customers can browse menus, place orders from numbered tables, and track their orders in real-time while vendors manage orders through live dashboards.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2-green.svg)
![Channels](https://img.shields.io/badge/channels-4.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### 👥 **Customer Experience**
- **📱 Menu-First Landing Page** - Browse all food and drinks immediately
- **🪑 Smart Table Selection** - Choose from 25 numbered tables
- **🛒 Real-time Shopping Cart** - Add items with floating cart indicator
- **📞 Simple Ordering** - Place orders with just name and phone number
- **📍 Browser Recovery** - Returns to saved table if browser is closed
- **⚡ Live Order Tracking** - Real-time status updates via WebSockets
- **🔔 Push Notifications** - Get notified when orders are ready

### 👨‍🍳 **Vendor Management**
- **📊 Real-time Dashboard** - Live order management interface
- **🔄 Instant Status Updates** - Change order/item status with immediate sync
- **🎵 Audio Notifications** - Sound alerts for new orders
- **📋 Menu Management** - Toggle item availability on-the-fly
- **🍳 Kitchen Display** - Centralized view of all active orders
- **📈 Order Statistics** - Track pending, preparing, and ready orders

### 🏗️ **Technical Features**
- **⚡ Real-time WebSockets** - Powered by Django Channels
- **🔴 Redis Integration** - Smart fallback to in-memory if Redis unavailable
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **🎨 Modern UI** - DaisyUI + TailwindCSS with dark theme
- **🧩 Component-based** - Alpine.js for reactive components
- **🔒 Secure** - CSRF protection and user authentication
- **📊 RESTful APIs** - Clean API endpoints for all operations

## 🚀 Quick Start

### **Option 1: Automated Setup (Recommended)**

```bash
cd river_side
python start_server.py
```

The script will automatically:
- ✅ Check dependencies and install if missing
- ✅ Set up database and run migrations
- ✅ Create sample data (tables, vendors, menu items)
- ✅ Create admin user (admin/admin123)
- ✅ Start the development server
- ✅ Open browser to the application

### **Option 2: Manual Setup**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py makemigrations
python manage.py migrate

# 3. Create sample data
python manage.py create_sample_data

# 4. Create superuser
python create_superuser.py

# 5. Start server
python manage.py runserver
```

## 📋 Sample Data

The system comes with comprehensive sample data:

### 🪑 **Tables**
- **25 numbered tables** (1-25)
- **Occupancy tracking** - Shows available/busy status
- **Seat capacity** - 2, 4, 6, or 8 seats per table

### 🏪 **Vendors**

#### 🥤 **Fresh Juice & Coffee Bar** (Drinks Vendor)
- **Fresh Juices**: Orange, Apple, Carrot Ginger, Green Juice, Watermelon
- **Coffee & Tea**: Cappuccino, Latte, Americano, Cold Brew, Green Tea, Chai Latte
- **Smoothies**: Mango, Berry Blast, Green Power, Tropical Paradise

#### 🍜 **Asian Delights** (Food Vendor)
- **Noodles**: Pad Thai, Chicken Lo Mein, Vegetable Ramen, Beef Chow Fun, Singapore Rice Noodles
- **Rice Dishes**: Chicken Fried Rice, Thai Basil Fried Rice, Korean Bibimbap, Teriyaki Chicken Bowl
- **Appetizers**: Spring Rolls, Chicken Satay, Pork Dumplings, Edamame

#### 🍕 **Pizza Corner** (Food Vendor)
- **Pizzas**: Margherita, Pepperoni, Hawaiian, Meat Lovers, Veggie Supreme, BBQ Chicken
- **Pasta**: Spaghetti Carbonara, Penne Arrabiata, Fettuccine Alfredo, Chicken Parmigiana

### 📊 **Menu Item Features**
- **Detailed descriptions** with ingredients
- **Dietary information** (vegetarian, vegan, spicy)
- **Nutritional data** (calories)
- **Preparation times** (3-20 minutes)
- **Dynamic pricing** ($2.50 - $19.90)

## 🔗 Access Points

Once the server is running, access different parts of the system:

| Interface | URL | Description |
|-----------|-----|-------------|
| 🏠 **Customer Menu** | `http://localhost:8000/` | Main landing page with menu and ordering |
| 👨‍🍳 **Vendor Dashboard** | `http://localhost:8000/vendors/` | Vendor management interface |
| 🍳 **Kitchen Display** | `http://localhost:8000/vendors/kitchen/` | Central kitchen order display |
| ⚙️ **Admin Panel** | `http://localhost:8000/admin/` | Django admin interface |
| 📊 **API Status** | `http://localhost:8000/api/status/` | System health check |

### 🔑 **Default Credentials**
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@riverside.com`

## 🎯 User Workflows

### 👤 **Customer Journey**

1. **🌐 Visit Landing Page** - Browse menu with all vendors
2. **🪑 Select Table** - Choose from available tables (1-25)
3. **🛒 Add Items** - Browse categories and add items to cart
4. **💳 Place Order** - Enter name and phone number
5. **📱 Track Order** - Real-time status updates
6. **🔔 Get Notified** - Receive alerts when order is ready

### 👨‍🍳 **Vendor Workflow**

1. **📊 Access Dashboard** - View real-time orders
2. **✅ Confirm Orders** - Accept incoming orders
3. **🍳 Start Preparing** - Update status to "preparing"
4. **✅ Mark Ready** - Notify customer when complete
5. **📋 Manage Menu** - Toggle item availability
6. **📈 Track Stats** - Monitor order volume and status

### 🍳 **Kitchen Display**

- **📺 Central Display** - All active orders across vendors
- **⏰ Order Timing** - Shows order age and prep times
- **🏪 Vendor Grouping** - Orders organized by vendor
- **🔄 Auto-refresh** - Real-time updates without page reload

## 🛠️ Technical Architecture

### **Backend Stack**
- **🐍 Django 5.2** - Web framework
- **⚡ Django Channels** - WebSocket support
- **🔴 Redis** - Channel layer (with in-memory fallback)
- **🗄️ PostgreSQL/SQLite** - Database (auto-detection)
- **📧 Email Integration** - Resend API support

### **Frontend Stack**
- **🎨 TailwindCSS + DaisyUI** - Styling framework
- **🧩 Alpine.js** - Reactive components
- **⚡ HTMX** - Dynamic page updates
- **🌐 WebSockets** - Real-time communication
- **📱 Responsive Design** - Mobile-first approach

### **Real-time Features**
```
Customer ←→ WebSocket ←→ Django Channels ←→ Redis ←→ Vendor Dashboard
    ↓                                                        ↓
Order Status Updates ←→ Kitchen Display ←→ Order Management
```

### **Database Models**

#### **Vendors App**
- `Vendor` - Food court vendors (drinks/food)
- `Category` - Menu categories per vendor
- `MenuItem` - Individual menu items with details
- `Table` - Numbered tables with capacity

#### **Orders App**
- `Order` - Customer orders with status tracking
- `OrderItem` - Individual items within orders
- `OrderStatusHistory` - Audit trail of status changes
- `Cart` - Session-based shopping cart
- `CartItem` - Items in customer cart

## 📱 API Endpoints

### **Public APIs**
```
GET  /api/status/                    # System health check
GET  /api/tables/                    # Available tables
POST /api/add-to-cart/              # Add item to cart
POST /api/update-cart-item/         # Update cart item quantity
POST /api/remove-from-cart/         # Remove cart item
POST /api/place-order/{table}/      # Place order for table
GET  /api/cart-status/{table}/      # Get cart status
```

### **Vendor APIs**
```
POST /vendors/{id}/api/update-order-status/    # Update order status
POST /vendors/{id}/api/update-item-status/     # Update item status
POST /vendors/{id}/api/toggle-menu-item/       # Toggle item availability
```

### **WebSocket Endpoints**
```
/ws/orders/table/{table_number}/     # Customer order updates
/ws/orders/vendor/{vendor_id}/       # Vendor order notifications
/ws/orders/kitchen/                  # Kitchen display updates
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Database
DB_NAME=river_view_dev
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (Optional)
RESEND_API_KEY=your-resend-api-key
```

### **Redis Configuration**
```python
# Automatic Redis detection with fallback
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',  # If Redis available
        # OR
        'BACKEND': 'channels.layers.InMemoryChannelLayer',   # Fallback
    },
}
```

## 🧪 Testing

### **Run Tests**
```bash
python manage.py test
```

### **Manual Testing**

1. **🔍 System Check**
   ```bash
   curl http://localhost:8000/api/status/
   ```

2. **📱 Customer Flow**
   - Visit `http://localhost:8000/`
   - Select table, add items, place order
   - Track order in real-time

3. **👨‍🍳 Vendor Flow**
   - Login to `http://localhost:8000/vendors/`
   - Update order status and watch real-time sync

## 🎨 Tailwind CSS Troubleshooting

If you're experiencing styling issues, here are common fixes:

### **Quick Fix Script**
```bash
python fix_tailwind.py
```

### **Manual Fixes**

#### **1. Rebuild Tailwind CSS**
```bash
python manage.py tailwind build
python manage.py collectstatic --noinput
```

#### **2. Check Template Tags**
Ensure your `base.html` has:
```html
{% load tailwind_cli %}
{% tailwind_css %}
```

#### **3. Verify Configuration**
Check `tailwind.config.js` content paths:
```javascript
content: [
  "./templates/**/*.html",
  "./orders/templates/**/*.html", 
  "./vendors/templates/**/*.html",
  // ... other paths
]
```

#### **4. Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| **No styling at all** | Run `python manage.py tailwind build` |
| **DaisyUI components missing** | Check `daisyui` plugin in `tailwind.config.js` |
| **Custom classes not working** | Verify `input.css` has `@tailwind` directives |
| **Static files not loading** | Run `python manage.py collectstatic` |

#### **5. Development Mode**
For real-time CSS rebuilding during development:
```bash
# Terminal 1: Watch for CSS changes
python manage.py tailwind watch

# Terminal 2: Run Django server  
python manage.py runserver
```

#### **6. Verify Installation**
```bash
# Check if Tailwind CLI is downloaded
python manage.py tailwind download_cli

# List available templates
python manage.py tailwind list_templates
```

#### **7. Reset Everything**
If all else fails:
```bash
# Remove existing CSS
rm -rf assets/css/tailwind.css
rm -rf staticfiles/

# Rebuild everything
python manage.py tailwind build
python manage.py collectstatic --noinput
```

## 📦 Deployment

### **Production Checklist**
- [ ] Set `DEBUG=False`
- [ ] Configure proper database (PostgreSQL)
- [ ] Set up Redis server
- [ ] Configure static file serving
- [ ] Set secure SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up SSL/HTTPS
- [ ] Configure email backend

### **Docker Deployment** (Optional)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to branch** (`git push origin feature/AmazingFeature`)
5. **Open Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Team** - For the amazing web framework
- **Django Channels** - For WebSocket support
- **TailwindCSS + DaisyUI** - For beautiful styling
- **Alpine.js** - For reactive components
- **HTMX** - For seamless interactions

## 📞 Support

- **📧 Email**: support@riverside-foodcourt.com
- **🐛 Issues**: [GitHub Issues](https://github.com/yourusername/river-side-food-court/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/yourusername/river-side-food-court/discussions)

---

**Built with ❤️ for food courts everywhere** 🍽️