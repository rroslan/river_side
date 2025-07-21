# 🏞️ River Side Food Court

A modern Django-based food court ordering system where customers can select tables, enter their phone number, browse menus, and add items to their cart. Built with Django, TailwindCSS, DaisyUI, and Alpine.js.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2-green.svg)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-3.x-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### 👥 **Customer Experience**
- **🪑 Table Selection** - Choose from numbered tables with availability status
- **📞 Phone Input Step** - Enter contact details before ordering
- **🛒 Menu Browsing** - View drinks and food vendors with categories
- **🛍️ Add to Cart** - Simple cart functionality with floating cart display
- **🔄 Reset Function** - Clear selection and start over
- **📱 Responsive Design** - Works on desktop, tablet, and mobile

### 🏗️ **Technical Features**
- **🎨 Modern UI** - DaisyUI + TailwindCSS with dark theme
- **🧩 Alpine.js** - For interactive components
- **⚡ HTMX** - For dynamic page updates
- **🔒 Secure** - CSRF protection and session management
- **📊 RESTful APIs** - Clean API endpoints for cart operations

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
| 🛒 **Checkout** | `http://localhost:8000/table/{number}/checkout/` | Review and place order |
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
6. **🔄 Reset Option** - Clear selection and start over if needed

## 🛠️ Technical Architecture

### **Backend Stack**
- **🐍 Django 5.2** - Web framework
- **🗄️ SQLite** - Database (default)
- **📧 Session Management** - For customer data persistence

### **Frontend Stack**
- **🎨 TailwindCSS + DaisyUI** - Styling framework
- **🧩 Alpine.js** - Reactive components
- **⚡ HTMX** - Dynamic page updates
- **📱 Responsive Design** - Mobile-first approach

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
POST /api/clear-session/            # Clear customer session
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Database (SQLite by default)
DB_NAME=db.sqlite3

# Security
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
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
   - Use reset button to start over

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
- [x] Session management for customer data
- [x] Reset functionality to clear session
- [x] Responsive design with TailwindCSS
- [x] Admin interface for data management

### 🚧 **In Development**
- [ ] Checkout and order placement
- [ ] Order tracking system
- [ ] Real-time updates with WebSockets
- [ ] Vendor dashboard
- [ ] Kitchen display system
- [ ] Email notifications

### 📋 **Planned Features**
- [ ] QR code generation for tables
- [ ] Payment integration
- [ ] Order history
- [ ] Customer feedback system
- [ ] Analytics dashboard
- [ ] Multi-language support

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
- **TailwindCSS + DaisyUI** - For beautiful styling
- **Alpine.js** - For reactive components
- **HTMX** - For seamless interactions

## 📞 Support

- **🐛 Issues**: Create an issue in the repository
- **💬 Questions**: Use the discussions section

---

**Built with ❤️ for food courts everywhere** 🍽️