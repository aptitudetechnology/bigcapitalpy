
from flask import Blueprint, render_template # Keep render_template as it's used by the reports_dashboard.index route

# Define the main reports blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# Add index route for /reports
@reports_bp.route('/')
def index():
    """
    Main index route for the /reports section.
    """
    # Sample report_data structure matching template requirements
    report_data = {
        "total_revenue": 125000.00,
        "net_profit": 32000.00,
        "total_expenses": 93000.00,
        "accounts_receivable": 15000.00
    }
    # Optionally, provide an empty recent_reports list for template
    recent_reports = []
    return render_template('reports/index.html', report_data=report_data, recent_reports=recent_reports)

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
