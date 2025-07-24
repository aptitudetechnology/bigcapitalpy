from flask import Blueprint, redirect, url_for, render_template # Import redirect, url_for, render_template

# Define the main reports blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# The 'index' route definition is moved inside register_reports_blueprints
# to ensure all sub-blueprints are registered before its url_for calls.


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

    # Define the default index route for the /reports URL prefix *after* sub-blueprints are registered
    @reports_bp.route('/')
    def index():
        """
        Default index route for the /reports URL prefix.
        This route is defined here to ensure all sub-blueprints are registered
        before it attempts to render the template with nested url_for calls.
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
            'accounts_receivable': 0.00 
        }
        
        # Now render the template, as all sub-blueprint routes should be available
        return render_template('reports/index.html', report_data=report_data)

    # Register the main reports_bp with the app
    app.register_blueprint(reports_bp)
