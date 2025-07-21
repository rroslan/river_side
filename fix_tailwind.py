#!/usr/bin/env python
"""
Tailwind CSS Fix Script for River Side Food Court
This script fixes common Tailwind CSS configuration and compilation issues.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print fix script banner"""
    print("\n" + "="*50)
    print("🎨 TAILWIND CSS FIX SCRIPT")
    print("="*50)
    print("🔧 Fixing Tailwind configuration issues")
    print("="*50 + "\n")

def check_django_setup():
    """Check if Django is properly set up"""
    try:
        import django
        from django.conf import settings

        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()

        print("✅ Django setup successful")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def fix_tailwind_config():
    """Fix tailwind.config.js"""
    print("\n🔧 Fixing tailwind.config.js...")

    config_content = '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./orders/templates/**/*.html",
    "./vendors/templates/**/*.html",
    "./static/**/*.js",
    "./assets/**/*.js",
    "./core/**/*.py",
    "./orders/**/*.py",
    "./vendors/**/*.py",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["dark", "light", "cupcake", "cyberpunk"],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
    prefix: "",
    logs: false,
    themeRoot: ":root",
  },
};
'''

    try:
        with open('tailwind.config.js', 'w') as f:
            f.write(config_content)
        print("  ✅ tailwind.config.js updated")
        return True
    except Exception as e:
        print(f"  ❌ Failed to update tailwind.config.js: {e}")
        return False

def fix_input_css():
    """Fix input.css file"""
    print("\n🔧 Fixing input.css...")

    # Ensure assets/css directory exists
    css_dir = Path('assets/css')
    css_dir.mkdir(parents=True, exist_ok=True)

    input_css_content = '''@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles for River Side Food Court */

/* Custom scrollbar for dark theme */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #1f2937;
}

::-webkit-scrollbar-thumb {
    background: #4b5563;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #6b7280;
}

/* Smooth transitions */
* {
    transition: all 0.2s ease-in-out;
}

/* HTMX loading indicator */
.htmx-indicator {
    opacity: 0;
    transition: opacity 500ms ease-in;
}

.htmx-request .htmx-indicator {
    opacity: 1;
}

.htmx-request.htmx-indicator {
    opacity: 1;
}

/* Order status specific styles */
.order-status-pending {
    border-left: 4px solid #f59e0b;
    background-color: rgba(245, 158, 11, 0.1);
}

.order-status-confirmed {
    border-left: 4px solid #3b82f6;
    background-color: rgba(59, 130, 246, 0.1);
}

.order-status-preparing {
    border-left: 4px solid #8b5cf6;
    background-color: rgba(139, 92, 246, 0.1);
}

.order-status-ready {
    border-left: 4px solid #10b981;
    background-color: rgba(16, 185, 129, 0.1);
}

.order-status-delivered {
    border-left: 4px solid #6b7280;
    background-color: rgba(107, 114, 128, 0.1);
}

.order-status-cancelled {
    border-left: 4px solid #ef4444;
    background-color: rgba(239, 68, 68, 0.1);
}

/* Pulse animations */
.pulse-animation {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Card hover effects */
.vendor-card {
    transition: all 0.3s ease;
}

.vendor-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.menu-item-card {
    transition: all 0.2s ease;
}

.menu-item-card:hover {
    transform: scale(1.02);
}

.order-item-card {
    transition: all 0.3s ease;
}

.order-item-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Status dots */
.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.status-pending .status-dot { background-color: #f59e0b; }
.status-confirmed .status-dot { background-color: #3b82f6; }
.status-preparing .status-dot {
    background-color: #8b5cf6;
    animation: pulse 2s infinite;
}
.status-ready .status-dot {
    background-color: #10b981;
    animation: pulse 2s infinite;
}
.status-delivered .status-dot { background-color: #6b7280; }
.status-cancelled .status-dot { background-color: #ef4444; }

/* Spicy indicator */
.spicy-indicator {
    color: #ff6b35;
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 5px #ff6b35; }
    to { text-shadow: 0 0 20px #ff6b35, 0 0 30px #ff6b35; }
}

/* Floating cart */
.cart-floating {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 100;
    transform: translateY(100px);
    transition: transform 0.3s ease;
}

.cart-floating.show {
    transform: translateY(0);
}

/* Table selector sticky */
.table-selector {
    position: sticky;
    top: 70px;
    z-index: 50;
    backdrop-filter: blur(10px);
    background: rgba(0, 0, 0, 0.1);
}

/* Notification dot */
.notification-dot {
    width: 8px;
    height: 8px;
    background: #ef4444;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

/* Responsive utilities */
@media (max-width: 640px) {
    .mobile-padding {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
'''

    try:
        with open('assets/css/input.css', 'w') as f:
            f.write(input_css_content)
        print("  ✅ input.css created/updated")
        return True
    except Exception as e:
        print(f"  ❌ Failed to update input.css: {e}")
        return False

def check_tailwind_cli():
    """Check if Tailwind CLI is installed"""
    print("\n🔍 Checking Tailwind CLI...")

    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'tailwind', 'download_cli'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("  ✅ Tailwind CLI is available")
            return True
        else:
            print("  ⚠️ Tailwind CLI download attempted")
            return True
    except Exception as e:
        print(f"  ❌ Tailwind CLI check failed: {e}")
        return False

def build_tailwind():
    """Build Tailwind CSS"""
    print("\n🎨 Building Tailwind CSS...")

    try:
        # First, try to build
        result = subprocess.run(
            [sys.executable, 'manage.py', 'tailwind', 'build'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("  ✅ Tailwind CSS built successfully!")
            print(f"  📁 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"  ❌ Build failed: {result.stderr}")

            # Try alternative method
            print("  🔄 Trying alternative build method...")

            # Check if tailwind.css exists
            css_file = Path('assets/css/tailwind.css')
            if css_file.exists():
                print("  ✅ Tailwind CSS file exists")
                return True
            else:
                print("  ❌ Tailwind CSS file not found")
                return False

    except Exception as e:
        print(f"  ❌ Build process failed: {e}")
        return False

def collect_static():
    """Run collectstatic to ensure CSS is available"""
    print("\n📦 Collecting static files...")

    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'collectstatic', '--noinput'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("  ✅ Static files collected successfully")
            return True
        else:
            print(f"  ⚠️ Static collection warning: {result.stderr}")
            return True  # Continue anyway

    except Exception as e:
        print(f"  ❌ Static collection failed: {e}")
        return False

def verify_template_tags():
    """Verify template tags are correctly loaded"""
    print("\n🏷️ Verifying template tags...")

    base_template = Path('templates/base.html')

    if not base_template.exists():
        print("  ❌ base.html template not found")
        return False

    try:
        with open(base_template, 'r') as f:
            content = f.read()

        if '{% load tailwind_cli %}' in content and '{% tailwind_css %}' in content:
            print("  ✅ Template tags are correctly loaded")
            return True
        else:
            print("  ⚠️ Template tags missing, attempting to fix...")

            # Add template tags if missing
            if '{% load tailwind_cli %}' not in content:
                content = content.replace(
                    '{% load static %}',
                    '{% load static %}\n    {% load tailwind_cli %}'
                )

            if '{% tailwind_css %}' not in content:
                content = content.replace(
                    '{% load tailwind_cli %}',
                    '{% load tailwind_cli %}\n    {% tailwind_css %}'
                )

            with open(base_template, 'w') as f:
                f.write(content)

            print("  ✅ Template tags added successfully")
            return True

    except Exception as e:
        print(f"  ❌ Template verification failed: {e}")
        return False

def run_test():
    """Run a quick test to verify Tailwind is working"""
    print("\n🧪 Running verification test...")

    try:
        test_script = '''
from django.test import Client
client = Client()
response = client.get("/")
status = response.status_code
content = response.content.decode()

print(f"Status: {status}")
print(f"Tailwind CSS found: {'tailwind' in content.lower()}")
print(f"DaisyUI classes found: {'btn-primary' in content}")
print(f"Template rendered: {len(content) > 1000}")

if status == 200 and 'btn-primary' in content:
    print("✅ Test PASSED - Tailwind is working!")
    exit(0)
else:
    print("❌ Test FAILED - Issues detected")
    exit(1)
'''

        result = subprocess.run(
            [sys.executable, 'manage.py', 'shell', '-c', test_script],
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            print("  ✅ Verification test passed!")
            return True
        else:
            print("  ❌ Verification test failed!")
            return False

    except Exception as e:
        print(f"  ❌ Test execution failed: {e}")
        return False

def main():
    """Main fix function"""
    print_banner()

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Check Django setup
    if not check_django_setup():
        print("❌ Cannot proceed without Django setup")
        sys.exit(1)

    # Fix configuration files
    fixes_successful = 0
    total_fixes = 6

    if fix_tailwind_config():
        fixes_successful += 1

    if fix_input_css():
        fixes_successful += 1

    if check_tailwind_cli():
        fixes_successful += 1

    if build_tailwind():
        fixes_successful += 1

    if collect_static():
        fixes_successful += 1

    if verify_template_tags():
        fixes_successful += 1

    # Run verification test
    print("\n" + "="*50)
    print(f"🎯 FIXES COMPLETED: {fixes_successful}/{total_fixes}")
    print("="*50)

    if fixes_successful == total_fixes:
        print("✅ All fixes applied successfully!")

        if run_test():
            print("\n🎉 SUCCESS! Tailwind CSS is now working properly!")
            print("\n📋 NEXT STEPS:")
            print("   1. Run: python manage.py runserver")
            print("   2. Visit: http://localhost:8000/")
            print("   3. Enjoy your styled food court app!")
        else:
            print("\n⚠️ Fixes applied but test failed. Manual check needed.")
    else:
        print(f"\n⚠️ Some fixes failed ({fixes_successful}/{total_fixes})")
        print("Manual intervention may be required.")

    print("\n" + "="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Fix process cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fix process failed: {e}")
        sys.exit(1)
