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
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import application modules
from packages.server.src.database import db
from packages.server.src.models import User, Organization
from packages.webapp.src.routes import register_blueprints

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
        """Format currency amounts"""
        if amount is None:
            return '$0.00'
        return f'${amount:,.2f}'
    
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
        return f'${amount:,.2f}'
    
    # Register blueprints
    register_blueprints(app)
    
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Starting BigCapitalPy...")
    print(f"📍 Running on http://localhost:{port}")
    print("💡 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
