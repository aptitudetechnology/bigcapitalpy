#!/usr/bin/env python3
"""
BigCapitalPy - Main Application Entry Point
A Python-based accounting software using Flask, HTML, CSS, and vanilla JavaScript

This is a complete rewrite of BigCapital with the following features:
- Flask backend with SQLAlchemy ORM
- HTML/CSS/JS frontend (no React)
- Modular architecture
- REST API
- Multi-tenancy support
- Financial reporting
- Inventory management
- Customer/Vendor management
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from datetime import datetime
from jinja2 import Undefined


print("Current working directory:", os.getcwd())

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import application modules
from packages.server.src.database import db
from packages.server.src.models import User, Organization
from packages.webapp.src.routes import register_blueprints
from packages.webapp.src.api import register_api_blueprints

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='packages/webapp/src/templates',
                static_folder='packages/webapp/src/static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bigcapitalpy.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf = CSRFProtect(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Custom Jinja2 filters
    @app.template_filter('datetime')
    def datetime_filter(dt, format='%B %d, %Y'):
        """Format datetime objects in templates"""
        if dt is None:
            return ''
        return dt.strftime(format)
    
    @app.template_filter('dateformat')
    def dateformat_filter(dt, format='%B %d, %Y'):
        """Format date objects in templates"""
        if dt is None:
            return ''
        if hasattr(dt, 'strftime'):
            return dt.strftime(format)
        return str(dt)
    
    @app.template_filter('currency')
    def currency_filter(amount):
        """Format currency amounts, handling None, empty values, and Jinja2 Undefined objects"""
        # Check for Jinja2 Undefined objects
        if isinstance(amount, Undefined):
            return '$0.00'
        
        # Handle None, empty string, or other falsy values
        if amount is None or amount == '' or amount == 0:
            return '$0.00'
        
        try:
            # Convert to float and format with thousands separator
            amount_float = float(amount)
            return f'${amount_float:,.2f}'
        except (ValueError, TypeError, AttributeError):
            # If conversion fails, return default value
            return '$0.00'
    
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks"""
        if not text:
            return ''
        return text.replace('\n', '<br>')
    
    # Template globals
    @app.template_global()
    def today():
        """Get today's date for templates"""
        from datetime import date
        return date.today
    
    # Add template helper for safe attribute access
    @app.template_global()
    def safe_get(obj, attr, default=''):
        """Safely get attribute from object with default fallback"""
        try:
            if hasattr(obj, attr):
                return getattr(obj, attr)
            elif isinstance(obj, dict) and attr in obj:
                return obj[attr]
            else:
                return default
        except:
            return default
    
    # Register blueprints
    register_blueprints(app)
    from packages.webapp.src.routes.estimates import estimates_bp
    app.register_blueprint(estimates_bp, url_prefix='/estimates')
    
    # Register API blueprints
    register_api_blueprints(app)
    
    # Create tables and sample data
    with app.app_context():
        db.create_all()
        
        # Create default organization if it doesn't exist
        if not Organization.query.first():
            org = Organization(
                name='Sample Company',
                currency='USD',
                fiscal_year_start='01-01',
                timezone='UTC'
            )
            db.session.add(org)
            
            # Create default admin user
            admin_user = User(
                email='admin@bigcapitalpy.com',
                first_name='Admin',
                last_name='User',
                password_hash=generate_password_hash('admin123'),
                is_active=True,
                role='admin',
                organization_id=1
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Default organization and admin user created")
            print("📧 Admin email: admin@bigcapitalpy.com")
            print("🔑 Admin password: admin123")
    
    # Health check endpoint for Docker
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}, 200

    # Dashboard route
    @app.route('/')
    def dashboard():
        return app.send_static_file('dashboard.html') if os.path.exists(os.path.join(app.static_folder, 'dashboard.html')) else render_template('dashboard.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Starting BigCapitalPy...")
    print(f"📍 Running on http://localhost:{port}")
    print("💡 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=port, debug=debug)