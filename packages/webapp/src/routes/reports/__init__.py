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
    # Import sub-blueprints that are confirmed to exist and define a blueprint object.
    from .tax import tax_bp
    from .sales import sales_bp
    from .financial import financial_bp
    from .expenses import expenses_bp
    # reports_dashboard_bp import and registration removed
    # Register sub-blueprints to the main reports_bp
    reports_bp.register_blueprint(tax_bp)
    reports_bp.register_blueprint(sales_bp)
    reports_bp.register_blueprint(financial_bp)
    reports_bp.register_blueprint(expenses_bp)
    
    # utils_bp was removed as it's not a Flask Blueprint.

    # Register the main reports_bp with the app
    app.register_blueprint(reports_bp)
