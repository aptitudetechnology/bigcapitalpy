from flask import Blueprint, render_template # Keep render_template as it's used by the reports_dashboard.index route

# Define the main reports blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# The 'index' route for /reports is defined in the reports_dashboard_bp
# and registered below.


def register_reports_blueprints(app):
    """
    Registers all report-related blueprints with the Flask application.
    Imports are placed inside this function to prevent circular import issues
    and ensure all sub-blueprints are registered before their routes are accessed.
    """
    # Import only the reports dashboard blueprint for now, as others caused ImportError.
    # Re-add other blueprint imports and registrations ONLY when you confirm their files exist
    # and contain the correct blueprint definitions.
    from .dashboard import reports_dashboard_bp 
    
    # Register only the reports dashboard blueprint to the main reports_bp for now.
    reports_bp.register_blueprint(reports_dashboard_bp)

    # Example of how to re-add other blueprints (uncomment and verify existence before adding):
    # from .tax import tax_bp
    # reports_bp.register_blueprint(tax_bp)
    # from .sales import sales_bp
    # reports_bp.register_blueprint(sales_bp)
    # from .financial import financial_bp
    # reports_bp.register_blueprint(financial_bp)
    # from .expenses import expenses_bp
    # reports_bp.register_blueprint(expenses_bp)
    # from .utils import utils_bp 
    # reports_bp.register_blueprint(utils_bp)

    # Register the main reports_bp with the app
    app.register_blueprint(reports_bp)
