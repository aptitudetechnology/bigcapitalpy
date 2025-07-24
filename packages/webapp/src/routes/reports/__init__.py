from flask import Blueprint, redirect, url_for, render_template # Import render_template

# Define the main reports blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# Define the index route for the main reports blueprint at the module level
@reports_bp.route('/')
def index():
    """
    Default index route for the /reports URL prefix.
    Renders the financial reports dashboard from reports/index.html.
    """
    # You can pass context variables if needed, e.g. report_data, recent_reports
    return render_template('reports/index.html')


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
