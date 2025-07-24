"""
Main blueprint registration for the BigCapitalPy web application.
This file registers all top-level blueprints with the Flask app instance.
"""

from flask import Blueprint

# Import individual blueprints (adjust these based on your actual project structure)
# If you have other top-level blueprints like auth, main, admin, etc., import them here.
# Example:
# from .auth import auth_bp
# from .main import main_bp
# from .admin import admin_bp
# from .vendors import vendors_bp
# from .customers import customers_bp
# from .items import items_bp
# from .invoices import invoices_bp
# from .bills import bills_bp
# from .dashboard import dashboard_bp # Assuming you have a main dashboard blueprint

# Import the reports blueprint registration function
from .reports import register_reports_blueprints


def register_blueprints(app):
    """
    Registers all application blueprints with the given Flask app instance.
    This function is called from app.py during application initialization.
    """
    # Register other top-level blueprints here
    # Example:
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(main_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(vendors_bp)
    # app.register_blueprint(customers_bp)
    # app.register_blueprint(items_bp)
    # app.register_blueprint(invoices_bp)
    # app.register_blueprint(bills_bp)
    # app.register_blueprint(dashboard_bp) # Register your main dashboard blueprint

    # Call the dedicated function to register all reports-related blueprints
    # This ensures that all sub-blueprints within 'reports' are set up correctly.
    register_reports_blueprints(app)

    # You can add more top-level blueprint registrations here if needed
