#!/usr/bin/env python3
"""
BigCapitalPy Quick Start Script
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    """Quick start for BigCapitalPy development"""

    parser = argparse.ArgumentParser(
        description="Quick start script for BigCapitalPy development and testing."
    )
    parser.add_argument(
        "--server",
        choices=["flask", "gunicorn"],
        default="flask",
        help="Choose the server to run the application (flask development server or gunicorn). Default: flask"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="The host address to bind the server to. Default: 127.0.0.1"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="The port to run the server on. Default: 5000"
    )
    parser.add_argument(
        "--https",
        action="store_true",
        help="Enable HTTPS. Requires --cert and --key if using gunicorn."
    )
    parser.add_argument(
        "--cert",
        help="Path to the SSL certificate file (e.g., cert.pem). Required for HTTPS with gunicorn."
    )
    parser.add_argument(
        "--key",
        help="Path to the SSL private key file (e.g., key.pem). Required for HTTPS with gunicorn."
    )

    args = parser.parse_args()

    print("🚀 BigCapitalPy - Python Accounting Software")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root.")
        sys.exit(1)

    # Check if virtual environment exists
    venv_path = Path('.venv')
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        result = subprocess.run([sys.executable, '-m', 'venv', '.venv'])
        if result.returncode != 0:
            print("❌ Failed to create virtual environment. Ensure your system's Python 3 is complete (e.g., 'sudo apt install python3-venv' on Ubuntu).")
            sys.exit(1)
        print("✅ Virtual environment created")

    # Determine the correct pip and python paths
    if os.name == 'nt':  # Windows
        pip_path = '.venv/Scripts/pip'
        python_path = '.venv/Scripts/python'
    else:  # Unix/Linux/MacOS
        pip_path = '.venv/bin/pip'
        python_path = '.venv/bin/python'
    
    # --- NEW STEP: Upgrade pip and setuptools within the venv ---
    print("⬆️ Upgrading pip and setuptools in the virtual environment...")
    result = subprocess.run([pip_path, 'install', '--upgrade', 'pip', 'setuptools'])
    if result.returncode == 0:
        print("✅ pip and setuptools upgraded successfully")
    else:
        print("❌ Failed to upgrade pip and setuptools. This might cause dependency installation issues.")
        # Don't exit here, as it might still work, but warn the user.
    # --- END NEW STEP ---

    # Install dependencies
    if os.path.exists('requirements-python.txt'):
        print("📥 Installing Python dependencies from requirements-python.txt...")
        # Ensure gunicorn is in requirements-python.txt if you plan to use --server gunicorn
        # Or install it explicitly here if not. For now, assume it's there or will be installed.
        result = subprocess.run([pip_path, 'install', '-r', 'requirements-python.txt'])
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print("❌ Failed to install dependencies. Check the error messages above.")
            sys.exit(1)
    
    # Set environment variables
    os.environ['FLASK_APP'] = 'app.py'
    # Keep development for now, but note that for production, it should be 'production'
    os.environ['FLASK_ENV'] = 'development' 
    
    print("\n🎯 Starting BigCapitalPy...")
    
    server_command = []
    protocol = "http"

    if args.https:
        protocol = "https"
        if args.server == "flask":
            print("⚠️ Warning: Running Flask development server with HTTPS is not recommended for performance or security.")
            print("⚠️ It's primarily for basic local testing. For better performance, use --server gunicorn.")
            # Flask's built-in server needs ssl_context directly in app.run()
            # This script runs app.py directly, so app.py itself would need to handle ssl_context.
            # For simplicity in this script, we'll assume app.py is configured for it
            # or recommend gunicorn for a more robust HTTPS setup.
            # For this script, we'll just inform the user and proceed with flask run.
            # The user's app.py would need to be modified to include:
            # app.run(ssl_context=('cert.pem', 'key.pem'))
            # For now, we'll just run it as is, and the user must configure app.py for SSL
            # if they insist on flask dev server with HTTPS.
            print(f"📍 The application will attempt to be available at: {protocol}://{args.host}:{args.port}")
            server_command = [python_path, 'app.py'] # Assumes app.py handles ssl_context internally
        elif args.server == "gunicorn":
            if not args.cert or not args.key:
                print("❌ Error: --cert and --key are required when enabling HTTPS with gunicorn.")
                sys.exit(1)
            print(f"📍 The application will be available at: {protocol}://{args.host}:{args.port}")
            server_command = [
                python_path, '-m', 'gunicorn',
                '-b', f'{args.host}:{args.port}',
                '--certfile', args.cert,
                '--keyfile', args.key,
                'app:app' # Assumes your Flask app instance is named 'app' in app.py
            ]
            print("💡 For production, it's highly recommended to use Nginx or Apache as a reverse proxy to handle SSL termination.")
            print("   This offloads the SSL overhead and provides better performance and security.")
    else:
        print(f"📍 The application will be available at: {protocol}://{args.host}:{args.port}")
        if args.server == "flask":
            server_command = [python_path, 'app.py']
        elif args.server == "gunicorn":
            server_command = [
                python_path, '-m', 'gunicorn',
                '-b', f'{args.host}:{args.port}',
                'app:app' # Assumes your Flask app instance is named 'app' in app.py
            ]

    print("📧 Demo login: admin@bigcapitalpy.com")
    print("🔑 Demo password: admin123")
    print("\n💡 Press Ctrl+C to stop the server")
    print("-" * 50)

    # Run the Flask application
    try:
        subprocess.run(server_command)
    except KeyboardInterrupt:
        print("\n👋 BigCapitalPy stopped. Thank you for using our software!")

if __name__ == '__main__':
    main()
