"""
Main blueprint registration for the BigCapitalPy web application.
This file registers all top-level blueprints with the Flask app instance.
"""

from flask import Blueprint

# Import only the top-level blueprints that are confirmed to exist
from .auth import auth_bp
from .dashboard import dashboard_bp
from .customers import customers_bp
from .vendors import vendors_bp
from .items import items_bp
from .invoices import invoices_bp
from .payments import payments_bp

from .accounts import accounts_bp
from .users import users_bp
from .organization import organization_bp
from .preferences import preferences_bp
from .backup import backup_bp

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

    # Now, register other top-level blueprints that are confirmed to exist.
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(vendors_bp, url_prefix='/vendors')
    app.register_blueprint(items_bp, url_prefix='/items')
    app.register_blueprint(invoices_bp, url_prefix='/invoices')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    app.register_blueprint(users_bp)
    app.register_blueprint(organization_bp, url_prefix='/organization')
    app.register_blueprint(preferences_bp, url_prefix='/preferences')
    app.register_blueprint(backup_bp, url_prefix='/backup')

    # The following blueprints were removed as they were reported as non-existent:
    # bills_bp, admin_bp, main_bp
