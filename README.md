# 🏞️ River Side Food Court

A modern Django-based food court ordering system where customers can select tables, enter their phone number, browse menus, and add items to their cart. Currently implementing real-time features with Django Channels, WebSockets, Redis, and Daphne for live order tracking and vendor notifications.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2-green.svg)
![Channels](https://img.shields.io/badge/channels-4.0-red.svg)
![Redis](https://img.shields.io/badge/redis-5.0-red.svg)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-3.x-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### 👥 **Customer Experience**
- **🪑 Table Selection** - Choose from numbered tables with availability status
- **📞 Phone Input Step** - Enter contact details before ordering
- **🛒 Menu Browsing** - View drinks and food vendors with categories
- **🛍️ Add to Cart** - Simple cart functionality with floating cart display
- **🛒 Cart Status Badge** - Real-time inline badge with item count and total price
- **📋 Checkout & Review** - Comprehensive order review with quantity controls
- **🔄 Complete Reset** - Clear all data (session, localStorage, database cart)
- **🛠️ Debug Tools** - Cart debugging and troubleshooting endpoints
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **⚡ Real-time Updates** - Live order status via WebSockets (in development)
- **🔔 Live Notifications** - Instant alerts for order updates (planned)

### 🏗️ **Technical Features**
- **🎨 Modern UI** - DaisyUI + TailwindCSS with dark theme
- **🧩 Alpine.js** - For interactive components
- **⚡ HTMX** - For dynamic page updates
- **🔒 Secure** - CSRF protection and session management
- **📊 RESTful APIs** - Clean API endpoints for cart operations
- **🌐 WebSocket Integration** - Real-time communication with Django Channels (planned)
- **🔴 Redis Backend** - Channel layer for WebSocket message routing (planned)
- **🚀 Daphne Server** - ASGI server for handling WebSocket connections (planned)
- **🔍 Debug Endpoints** - Cart inspection and troubleshooting tools

## 🚀 Quick Start

### **Automated Setup (Recommended)**

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

### **Manual Setup**

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
| 🏠 **Table Selection** | `http://localhost:8000/` | Landing page for table selection |
| 👤 **Phone Input** | `http://localhost:8000/table/{number}/` | Customer contact details |
| 🍽️ **Menu** | `http://localhost:8000/table/{number}/menu/` | Browse and order from menu |
| 🛒 **Checkout** | `http://localhost:8000/table/{number}/checkout/` | Review cart and place order |
| 📊 **Track Orders** | `http://localhost:8000/table/{number}/track/` | Order status tracking |
| ⚙️ **Admin Panel** | `http://localhost:8000/admin/` | Django admin interface |
| 📊 **API Status** | `http://localhost:8000/api/status/` | System health check |

### 🔑 **Default Credentials**
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@riverside.com`

## 🎯 User Workflow

### 👤 **Customer Journey**

1. **🏠 Landing Page** - View available tables with occupancy status
2. **🪑 Select Table** - Choose from numbered tables (1-25)
3. **📞 Enter Details** - Provide phone number and optional name
4. **🍽️ Browse Menu** - View drinks and food vendors with categories
5. **🛒 Add Items** - Add items to cart with floating cart indicator
6. **📊 Cart Status** - See real-time cart count and total in header badge
7. **📋 Checkout** - Review order, adjust quantities, add special instructions
8. **💳 Place Order** - Submit order with loading and success confirmation
9. **🔄 Complete Reset** - Clear all data (session, cart, localStorage) and restart
10. **⚡ Real-time Tracking** - Live order status updates (in development)
11. **🔔 Notifications** - Get notified when order status changes (planned)

## 🛠️ Technical Architecture

### **Backend Stack**
- **🐍 Django 5.2** - Web framework
- **⚡ Django Channels 4.0** - WebSocket support and async handling
- **🔴 Redis 5.0** - Channel layer backend for WebSocket message routing
- **🚀 Daphne** - ASGI server for handling HTTP and WebSocket connections
- **🗄️ SQLite/PostgreSQL** - Database (SQLite for dev, PostgreSQL for production)
- **📧 Session Management** - For customer data persistence

### **Frontend Stack**
- **🎨 TailwindCSS + DaisyUI** - Styling framework
- **🧩 Alpine.js** - Reactive components
- **⚡ HTMX** - Dynamic page updates
- **🌐 WebSockets** - Real-time communication with server
- **📱 Responsive Design** - Mobile-first approach

### **Real-time Communication Flow**
```
Customer Browser ←→ WebSocket ←→ Django Channels ←→ Redis ←→ Vendor Dashboard
       ↓                                                           ↓
   Order Updates ←→ WebSocket Consumer ←→ Channel Groups ←→ Kitchen Display
```

### **Database Models**

#### **Vendors App**
- `Vendor` - Food court vendors (drinks/food)
- `Category` - Menu categories per vendor
- `MenuItem` - Individual menu items with details
- `Table` - Numbered tables with capacity and occupancy

#### **Orders App**
- `Order` - Customer orders with contact information
- `OrderItem` - Individual items within orders
- `Cart` - Session-based shopping cart
- `CartItem` - Items in customer cart

## 📱 API Endpoints

### **Customer APIs**
```
GET  /api/status/                    # System health check
GET  /api/tables/                    # Available tables
POST /api/add-to-cart/              # Add item to cart
POST /api/update-cart-item/         # Update cart item quantity
POST /api/remove-from-cart/         # Remove cart item
POST /api/place-order/{table}/      # Place order for table
GET  /api/cart-status/{table}/      # Get cart status
GET  /api/items-status/{table}/     # Get order status
POST /api/clear-session/            # Clear session and cart data
```

### **🔍 Debug Endpoints**
```
GET  /debug/cart/{table_number}/         # Inspect cart contents
GET  /debug/clear-cart/{table_number}/   # Clear cart for testing
```

### **WebSocket Endpoints (In Development)**
```
/ws/orders/table/{table_number}/     # Customer order updates
/ws/orders/vendor/{vendor_id}/       # Vendor order notifications  
/ws/orders/kitchen/                  # Kitchen display updates
/ws/orders/status/{order_id}/        # Order status tracking
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Database (SQLite by default, PostgreSQL for production)
DB_NAME=db.sqlite3
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/1
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1

# Security
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ASGI/WebSocket Settings
ASGI_APPLICATION=core.asgi.application
```

### **Redis & Channels Configuration**
```python
# Channel layers configuration in settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Fallback for development without Redis
if not REDIS_AVAILABLE:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }
```

### **Daphne Server Setup**
```bash
# For development with WebSockets
daphne -b 0.0.0.0 -p 8000 core.asgi:application

# Or use Django's built-in ASGI support
python manage.py runserver
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
   - Select an available table
   - Enter phone number
   - Browse menu and add items to cart
   - See real-time cart status in header badge
   - Review order in checkout with quantity controls
   - Place order and get confirmation
   - Use reset button for complete fresh start
   - Debug cart issues with /debug/cart/{table}/ if needed

## 🎨 Tailwind CSS Setup

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

#### **3. Development Mode**
For real-time CSS rebuilding during development:
```bash
# Terminal 1: Watch for CSS changes
python manage.py tailwind watch

# Terminal 2: Run Django server  
python manage.py runserver
```

## 📂 Project Structure

```
river_side/
├── core/                   # Django project settings
├── orders/                 # Orders app (cart, orders)
├── vendors/                # Vendors app (vendors, tables, menu)
├── templates/              # HTML templates
│   ├── base.html          # Base template with TailwindCSS
│   ├── orders/            # Order-related templates
│   └── vendors/           # Vendor-related templates
├── static/                # Static files
├── media/                 # Media uploads
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
├── start_server.py       # Automated setup script
└── README.md             # This file
```

## 🚀 Current Implementation Status

### ✅ **Completed Features**
- [x] Table selection with occupancy status
- [x] Phone input step with validation
- [x] Menu display with vendor categories
- [x] Add to cart functionality
- [x] Floating cart indicator
- [x] Cart status badge (inline with customer info)
- [x] Comprehensive checkout page
- [x] Cart quantity controls (increase/decrease)
- [x] Remove items from cart
- [x] Order placement with confirmation
- [x] Special instructions for orders (compact UI)
- [x] Session management for customer data
- [x] Complete reset functionality (session + cart + localStorage)
- [x] Debug tools for cart troubleshooting
- [x] Cart data synchronization fixes
- [x] Responsive design with TailwindCSS
- [x] Admin interface for data management

### 🚧 **Currently Implementing (Real-time Features)**
- [ ] **Order Tracking System** - Live order status updates for customers  
- [ ] **Django Channels Setup** - WebSocket support for real-time communication
- [ ] **Redis Integration** - Channel layer backend for message routing
- [ ] **Daphne ASGI Server** - Production-ready WebSocket server
- [ ] **WebSocket Consumers** - Handle real-time order updates
- [ ] **Channel Groups** - Organize connections by table/vendor/kitchen
- [ ] **Real-time Order Status** - Live updates when orders change status
- [ ] **Vendor Notifications** - Instant alerts for new orders
- [ ] **Kitchen Display** - Live dashboard showing all active orders

### 🔧 **Recently Improved**
- [x] **Cart Data Consistency** - Fixed badge/checkout count discrepancies
- [x] **Enhanced Reset** - Now clears server-side cart data
- [x] **Debug Tools** - Cart inspection endpoints for troubleshooting
- [x] **UI Polish** - Compact special instructions textbox with proper sizing
- [x] **Form Optimization** - 50px height textbox with character limits and inline styles
- [x] **Order Workflow** - Better UX for pending vendor confirmations
- [x] **Success Modal** - Clearer messaging about order confirmation process

### 🔄 **Next Phase Development**
- [ ] Order tracking system with live updates
- [ ] Vendor dashboard with real-time order management  
- [ ] Kitchen display system with live order feed
- [ ] Push notifications for order status changes
- [ ] Email notifications integration

### 🐛 **Bug Fixes This Session**
- [x] **Cart Count Inconsistency** - Fixed mismatch between badge and checkout
- [x] **Reset Incomplete** - Now clears database cart data, not just session
- [x] **Accumulated Test Data** - Debug tools to identify and clear old data
- [x] **UI Proportions** - Compact special instructions textbox (50px height)
- [x] **Form Consistency** - Unified textbox sizing across order modal and checkout
- [x] **Order Tracking UX** - Fixed empty tracking page confusion for pending orders
- [x] **Workflow Clarity** - Better messaging about vendor confirmation process

### 📋 **Future Enhancements**
- [ ] QR code generation for tables
- [ ] Payment integration (Stripe/PayPal)
- [ ] Order history and analytics
- [ ] Customer feedback system
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app development

## 🌐 Real-time Architecture Roadmap

### **Phase 1: WebSocket Foundation**
```python
# Consumer for handling customer connections
class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.table_number = self.scope['url_route']['kwargs']['table_number']
        self.table_group_name = f'table_{self.table_number}'
        
        await self.channel_layer.group_add(
            self.table_group_name,
            self.channel_name
        )
        await self.accept()
```

### **Phase 2: Vendor Integration**
```python
# Real-time order updates to vendors
async def send_order_update(order_id, status):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"vendor_{order.vendor_id}",
        {
            'type': 'order_update',
            'order_id': order_id,
            'status': status,
            'timestamp': timezone.now().isoformat()
        }
    )
```

### **Phase 3: Kitchen Display**
```python
# Kitchen display real-time updates
class KitchenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("kitchen_display", self.channel_name)
        await self.accept()
        
    async def order_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'order': event['order_data'],
            'action': event['action']  # 'new', 'update', 'complete'
        }))
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
- **Django Channels Team** - For WebSocket and async support
- **Redis** - For reliable message brokering
- **Daphne** - For ASGI server capabilities
- **TailwindCSS + DaisyUI** - For beautiful styling
- **Alpine.js** - For reactive components
- **HTMX** - For seamless interactions

## 📞 Support

- **🐛 Issues**: Create an issue in the repository
- **💬 Questions**: Use the discussions section

---

**Built with ❤️ for food courts everywhere** 🍽️