from flask import Blueprint, redirect, url_for, render_template # Import render_template

# Define the main reports blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# Define the index route for the main reports blueprint at the module level
@reports_bp.route('/')
def index():
    """
    Default index route for the /reports URL prefix.
    This route is defined at the module level to ensure it's available
    when url_for('reports.index') is called early in the application lifecycle.
    
    It will render a generic reports dashboard or redirect to a default report
    once all sub-blueprints are guaranteed to be registered.
    For now, we'll render a simple placeholder or a dedicated reports index template.
    """
    # Option 1: Render a dedicated reports index template (recommended for a proper UI)
    # You would need to create packages/webapp/src/templates/reports/index.html
    # return render_template('reports/index.html')

    # Option 2: Return a simple string placeholder for testing purposes
    return "<h1>Reports Home Page</h1><p>Welcome to the reports section. Please navigate to a specific report from the menu.</p>"


def register_reports_blueprints(app):
    """
    Registers all report-related blueprints with the Flask application.
    Imports are placed inside this function to prevent circular import issues.
    """
    # Import sub-blueprints here to avoid circular dependencies at module load time
    from .tax import tax_bp
    from .sales import sales_bp
    from .financial import financial_bp
    from .expenses import expenses_bp
    # If utils_bp is ever used as a blueprint, uncomment and import it here
    # from .utils import utils_bp 

    # Register sub-blueprints to the main reports_bp
    reports_bp.register_blueprint(tax_bp)
    reports_bp.register_blueprint(sales_bp)
    reports_bp.register_blueprint(financial_bp)
    reports_bp.register_blueprint(expenses_bp)
    # reports_bp.register_blueprint(utils_bp) # Uncomment if utils_bp is a blueprint to be registered

    # Register the main reports_bp with the app
    app.register_blueprint(reports_bp)
