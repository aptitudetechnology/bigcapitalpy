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

# Ensure the project root is in the Python path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) # Add current directory as well

from flask import Flask, render_template # Added render_template as it's used in dashboard route
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from datetime import datetime, date # Added date for today() global
from jinja2 import Undefined


print("Current working directory:", os.getcwd())


# Import application modules
# These imports must be after sys.path.insert to ensure they are found
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
    app.config['WTF_CSRF_ENABLED'] = False # Consider enabling CSRF protection for production

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf = CSRFProtect(app) # CSRFProtect needs app passed to it

    # Register custom Jinja2 filter after app is created
    # Note: The datetimeformat filter was defined twice, removed the first redundant one.
    def datetimeformat(value, format='%Y-%m-%d %H:%M'):
        if value is None:
            return ''
        try:
            # Ensure value is a datetime object, if not, convert if possible or handle
            if not isinstance(value, datetime):
                # Attempt to parse if it's a string, or just return as string
                try:
                    value = datetime.fromisoformat(str(value)) # Example for ISO format strings
                except ValueError:
                    return str(value) # Fallback if not a recognized datetime string
            return value.strftime(format)
        except Exception:
            return str(value) # Fallback for any other exceptions
    app.add_template_filter(datetimeformat, 'datetimeformat')

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
        # Use datetime.date.today directly, not a reference to it
        return date.today()

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

    # Health check endpoint for Docker
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}, 200

    # Dashboard route
    @app.route('/')
    def dashboard():
        # Check if dashboard.html exists in static, otherwise render from templates
        # This logic is a bit unusual. Typically, static files are for direct serving
        # and templates are for rendering with Jinja2.
        # If dashboard.html is a static HTML file, app.send_static_file is correct.
        # If it's a Jinja2 template, render_template is correct.
        # Assuming it's a Jinja2 template that might be served statically for simplicity.
        return render_template('dashboard.html')


    return app

# --- CRITICAL CHANGE HERE ---
# Call the application factory to create the app instance at the module level.
# This makes 'app' directly accessible when Gunicorn imports this module.
app = create_app()
# --- END CRITICAL CHANGE ---

if __name__ == '__main__':
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    # The 'app' variable is already created above, so no need to re-create it here.
    # We just use it for running the development server.
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    CERT_PATH = os.path.join(PROJECT_ROOT, 'ssl', 'cert.pem')
    KEY_PATH = os.path.join(PROJECT_ROOT, 'ssl', 'key.pem')

    logger.info(f"🚀 Starting BigCapitalPy on port {port}")
    logger.info(f"📍 Looking for SSL certs in: {CERT_PATH}, {KEY_PATH}")

    # Ensure database tables and sample data are created when running directly
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


    if os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
        logger.info("✅ SSL certificates found. Running in HTTPS mode.")
        app.run(host='0.0.0.0', port=port, debug=debug, ssl_context=(CERT_PATH, KEY_PATH))
    else:
        logger.warning("⚠️ SSL certificates not found. Running in HTTP mode.")
        logger.warning("💡 To enable HTTPS, generate them using:")
        logger.warning("   openssl genrsa -out ssl/key.pem 2048 && openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365")
        app.run(host='0.0.0.0', port=port, debug=debug)
