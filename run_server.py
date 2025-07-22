#!/usr/bin/env python
"""
River Side Food Court - Development Server with WebSocket Support

This script starts the Django development server with ASGI support for WebSockets.
Use this instead of 'python manage.py runserver' to enable real-time features.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_redis():
    """Check if Redis is available"""
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, db=0, socket_timeout=2)
        r.ping()
        print("✅ Redis is running - WebSocket performance will be optimal")
        return True
    except (redis.ConnectionError, redis.TimeoutError, ImportError):
        print("⚠️  Redis not available - using in-memory channels (development only)")
        print("💡 To install Redis: sudo apt-get install redis-server")
        return False

def run_server(host='127.0.0.1', port=8000, verbosity=1):
    """Run the development server with ASGI support"""

    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found. Run this script from the project root.")
        sys.exit(1)

    # Check Redis status
    check_redis()

    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    # Run migrations first
    print("\n🔄 Checking for database migrations...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ Database is up to date")
    except subprocess.CalledProcessError:
        print("⚠️  Migration check failed, but continuing...")

    # Start the ASGI server
    print(f"\n🚀 Starting River Side Food Court server with WebSocket support...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"🔌 WebSocket endpoint: ws://{host}:{port}/ws/")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)

    try:
        # Use daphne to run the ASGI application
        cmd = [
            sys.executable, '-m', 'daphne',
            '-b', host,
            '-p', str(port),
            '-v', str(verbosity),
            'core.asgi:application'
        ]

        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n💡 Fallback: Try running with standard Django server (no WebSockets):")
        print(f"   python manage.py runserver {host}:{port}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run River Side Food Court development server with WebSocket support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_server.py                    # Run on 127.0.0.1:8000
  python run_server.py -p 8080           # Run on port 8080
  python run_server.py -h 0.0.0.0        # Run on all interfaces
  python run_server.py -p 8080 -v 2      # Run with more verbose logging
        """
    )

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=8000,
        help='Port to run the server on (default: 8000)'
    )

    parser.add_argument(
        '-H', '--host',
        default='127.0.0.1',
        help='Host to bind the server to (default: 127.0.0.1)'
    )

    parser.add_argument(
        '-v', '--verbosity',
        type=int,
        choices=[0, 1, 2, 3],
        default=1,
        help='Verbosity level (0=minimal, 1=normal, 2=verbose, 3=debug)'
    )

    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check the setup without starting the server'
    )

    args = parser.parse_args()

    if args.check_only:
        print("🔍 Checking server setup...")
        check_redis()
        print("✅ Setup check complete")
        return

    run_server(args.host, args.port, args.verbosity)

if __name__ == '__main__':
    main()
