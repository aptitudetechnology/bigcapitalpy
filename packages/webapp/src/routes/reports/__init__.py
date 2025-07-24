from flask import Blueprint

# Define the main reports blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# The 'index' route for /reports will now be defined in a separate 'dashboard' blueprint
# and registered within the register_reports_blueprints function.


def register_reports_blueprints(app):
    """
    Registers all report-related blueprints with the Flask application.
    Imports are placed inside this function to prevent circular import issues
    and ensure all sub-blueprints are registered before their routes are accessed.
    """
    # Import sub-blueprints here to avoid circular dependencies at module load time
    from .tax import tax_bp
    from .sales import sales_bp
    from .financial import financial_bp
    from .expenses import expenses_bp
    # NEW: Import the dedicated reports dashboard blueprint
    from .dashboard import reports_dashboard_bp 
    # If utils_bp is ever used as a blueprint, uncomment and import it here
    # from .utils import utils_bp 

    # Register sub-blueprints to the main reports_bp
    reports_bp.register_blueprint(tax_bp)
    reports_bp.register_blueprint(sales_bp)
    reports_bp.register_blueprint(financial_bp)
    reports_bp.register_blueprint(expenses_bp)
    # NEW: Register the reports dashboard blueprint. This should be registered last
    # or strategically, so its index route can correctly resolve other sub-blueprint URLs.
    reports_bp.register_blueprint(reports_dashboard_bp)
    
    # reports_bp.register_blueprint(utils_bp) # Uncomment if utils_bp is a blueprint to be registered

    # Register the main reports_bp with the app
    app.register_blueprint(reports_bp)
