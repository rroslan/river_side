#!/usr/bin/env python
"""
River Side Food Court - Server Startup Script
This script handles the complete startup process for the food court system.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("\n" + "="*60)
    print("🏞️  RIVER SIDE FOOD COURT - STARTUP SCRIPT")
    print("="*60)
    print("🍽️  Real-time Food Court Management System")
    print("⚡  Django + Channels + WebSockets + Alpine.js")
    print("="*60 + "\n")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")

    required_packages = [
        'django',
        'channels',
        'redis',
        'pillow'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")

        # Try to install automatically
        try:
            print("\n🔧 Attempting to install missing packages...")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages,
                         check=True, capture_output=True)
            print("✅ Packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages automatically")
            print("   Please install manually: pip install -r requirements.txt")
            sys.exit(1)

def setup_database():
    """Set up database migrations"""
    print("\n🗄️  Setting up database...")

    try:
        # Check if migrations exist
        if not Path('vendors/migrations/0001_initial.py').exists():
            print("  📝 Creating migrations...")
            subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)

        # Run migrations
        print("  🔄 Running migrations...")
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("  ✅ Database migrations completed")
        else:
            print(f"  ❌ Migration failed: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

    return True

def create_sample_data():
    """Create sample data if database is empty"""
    print("\n🌱 Checking sample data...")

    try:
        # Check if we have data
        result = subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c',
            'from vendors.models import Vendor; print(Vendor.objects.count())'
        ], capture_output=True, text=True)

        vendor_count = int(result.stdout.strip().split('\n')[-1])

        if vendor_count == 0:
            print("  📊 Creating sample data...")
            subprocess.run([sys.executable, 'manage.py', 'create_sample_data'], check=True)
            print("  ✅ Sample data created!")
        else:
            print(f"  ✅ Found {vendor_count} vendors - data exists")

    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"  ⚠️  Could not check/create sample data: {e}")

def create_superuser():
    """Create superuser if it doesn't exist"""
    print("\n👤 Checking admin user...")

    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c',
            'from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())'
        ], capture_output=True, text=True)

        has_superuser = 'True' in result.stdout

        if not has_superuser:
            print("  🔑 Creating admin user...")
            subprocess.run([sys.executable, 'create_superuser.py'], check=True)
            print("  ✅ Admin user created!")
            print("     Username: admin")
            print("     Password: admin123")
        else:
            print("  ✅ Admin user exists")

    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Could not create admin user: {e}")

def check_redis():
    """Check if Redis is available"""
    print("\n🔴 Checking Redis...")

    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=2)
        r.ping()
        print("  ✅ Redis is available - Real-time features enabled")
        return True
    except:
        print("  ⚠️  Redis not available - Using in-memory channels")
        print("     Install Redis for better performance: sudo apt-get install redis-server")
        return False

def build_tailwind():
    """Build Tailwind CSS"""
    print("\n🎨 Building Tailwind CSS...")

    try:
        subprocess.run([sys.executable, 'manage.py', 'tailwind', 'build'], check=True)
        print("  ✅ Tailwind CSS built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Tailwind build failed: {e}")
        print("     Continuing anyway - CSS may not be styled properly")
        return False

def start_development_server():
    """Start the Django development server"""
    print("\n🚀 Starting development server...")
    print("="*60)

    # Print access information
    print("\n📱 ACCESS INFORMATION:")
    print("   🏠 Customer Menu:     http://localhost:8000/")
    print("   👨‍🍳 Vendor Dashboard:  http://localhost:8000/vendors/")
    print("   🍳 Kitchen Display:   http://localhost:8000/vendors/kitchen/")
    print("   ⚙️  Admin Panel:      http://localhost:8000/admin/")
    print("   📊 Status Check:     http://localhost:8000/api/status/")

    print("\n🔑 DEFAULT CREDENTIALS:")
    print("   Username: admin")
    print("   Password: admin123")

    print("\n📝 SAMPLE DATA:")
    print("   📋 25 Tables (1-25)")
    print("   🏪 3 Vendors (Drinks, Asian, Pizza)")
    print("   🍽️  38 Menu Items")
    print("   📦 10 Sample Orders")

    print("\n🎨 STYLING:")
    print("   🌙 Dark theme by default")
    print("   🎨 TailwindCSS + DaisyUI components")
    print("   📱 Fully responsive design")

    print("\n" + "="*60)
    print("🎯 QUICK START GUIDE:")
    print("   1. Open http://localhost:8000/ for customer view")
    print("   2. Select a table (1-25)")
    print("   3. Add items to cart and place order")
    print("   4. Use /vendors/ for vendor management")
    print("   5. Press Ctrl+C to stop the server")
    print("="*60 + "\n")

    # Auto-open browser
    try:
        webbrowser.open('http://localhost:8000/')
        print("🌐 Opening browser...")
    except:
        pass

    try:
        # Start server
        os.execv(sys.executable, [sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using River Side Food Court!")
        sys.exit(0)

def main():
    """Main startup function"""
    print_banner()

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # System checks
    check_python_version()
    check_dependencies()

    # Database setup
    if not setup_database():
        print("❌ Database setup failed. Please check the errors above.")
        sys.exit(1)

    # Data setup
    create_sample_data()
    create_superuser()

    # Build Tailwind CSS
    build_tailwind()

    # Service checks
    redis_available = check_redis()

    # Final system check
    print("\n🔍 Running system check...")
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'check'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ System check passed")
        else:
            print(f"  ⚠️  System check warnings: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ System check failed: {e}")
        sys.exit(1)

    # Start server
    print("\n✨ All systems ready!")
    time.sleep(1)
    start_development_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Startup cancelled. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        print("Please check the error and try again.")
        sys.exit(1)
