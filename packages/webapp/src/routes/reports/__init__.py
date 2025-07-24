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
    
    It will now render the 'reports/index.html' template and pass a placeholder
    'report_data' dictionary to avoid 'UndefinedError'.
    """
    # Provide a placeholder or empty report_data dictionary
    # You might want to fetch actual summary data here in a real application
    report_data = {
        'total_revenue': 0.00,
        'total_expenses': 0.00,
        'net_profit': 0.00,
        'total_sales_invoices': 0,
        'total_purchase_bills': 0,
        'cash_balance': 0.00,
        'unreconciled_transactions': 0,
        'accounts_receivable': 0.00 # Added this key with a default value
    }
    
    return render_template('reports/index.html', report_data=report_data)


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
