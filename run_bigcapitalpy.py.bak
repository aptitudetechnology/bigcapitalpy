#!/usr/bin/env python3
"""
BigCapitalPy Quick Start Script
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Quick start for BigCapitalPy development"""
    
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
        result = subprocess.run([pip_path, 'install', '-r', 'requirements-python.txt'])
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print("❌ Failed to install dependencies. Check the error messages above.")
            sys.exit(1)
    
    # Set environment variables
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    print("\n🎯 Starting BigCapitalPy...")
    print("📍 The application will be available at: http://localhost:5000")
    print("📧 Demo login: admin@bigcapitalpy.com")
    print("🔑 Demo password: admin123")
    print("\n💡 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the Flask application
    try:
        subprocess.run([python_path, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 BigCapitalPy stopped. Thank you for using our software!")

if __name__ == '__main__':
    main()