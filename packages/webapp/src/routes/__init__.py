"""
Main blueprint registration for the BigCapitalPy web application.
This file registers all top-level blueprints with the Flask app instance.
"""

from flask import Blueprint

# Import individual blueprints (adjust these based on your actual project structure)
# Ensure ALL top-level blueprints are imported here.
# Removed 'from .main import main_bp' as it caused a ModuleNotFoundError.
from .auth import auth_bp
from .admin import admin_bp
from .vendors import vendors_bp
from .customers import customers_bp
from .items import items_bp
from .invoices import invoices_bp
from .bills import bills_bp
from .dashboard import dashboard_bp # Assuming your main dashboard blueprint is here

# Import the reports blueprint registration function
from .reports import register_reports_blueprints


def register_blueprints(app):
    """
    Registers all application blueprints with the given Flask app instance.
    This function is called from app.py during application initialization.
    """
    # CRITICAL: Register reports blueprints FIRST if other blueprints' templates
    # (like base.html used by dashboard) rely on reports URLs.
    register_reports_blueprints(app)

    # Now, register other top-level blueprints.
    # Removed 'app.register_blueprint(main_bp)' as it caused a ModuleNotFoundError.
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(bills_bp)
    app.register_blueprint(dashboard_bp) 

    # Add any other top-level blueprint registrations here if you have them.
