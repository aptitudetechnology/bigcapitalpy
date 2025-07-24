"""
Main blueprint registration for the BigCapitalPy web application.
This file registers all top-level blueprints with the Flask app instance.
"""

from flask import Blueprint

# Import individual blueprints (adjust these based on your actual project structure)
# Only keep imports for blueprints that genuinely exist in your project.
# Removed 'main_bp', 'admin_bp', 'bills_bp' to resolve ModuleNotFoundErrors.

from .auth import auth_bp # Keep this if auth_bp exists
from .dashboard import dashboard_bp # Keep this if dashboard_bp exists
from .customers import customers_bp # Already re-added
from .vendors import vendors_bp # Already re-added
from .items import items_bp # Already re-added
from .invoices import invoices_bp # Already re-added
from .payments import payments_bp # Already re-added
from .accounts import accounts_bp # RE-ADDED: Ensure packages/webapp/src/routes/accounts.py exists and defines 'accounts_bp'

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
    # Registering auth_bp, dashboard_bp, customers_bp, vendors_bp, items_bp, invoices_bp, payments_bp, and accounts_bp.
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp) 
    app.register_blueprint(customers_bp) 
    app.register_blueprint(vendors_bp) 
    app.register_blueprint(items_bp) 
    app.register_blueprint(invoices_bp) 
    app.register_blueprint(payments_bp) 
    app.register_blueprint(accounts_bp) # RE-ADDED: Register the accounts_bp

    # If you have other top-level blueprints (e.g., for bills, admin, main)
    # and their files *do* exist, you will need to re-add their imports
    # and app.register_blueprint() calls here.
    # Example (uncomment and verify existence before adding):
    # from .bills import bills_bp
    # app.register_blueprint(bills_bp)
    # from .admin import admin_bp
    # app.register_blueprint(admin_bp)
    # from .main import main_bp
    # app.register_blueprint(main_bp)

    # Add any other top-level blueprint registrations here if you have them.
