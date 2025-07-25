
from flask import Blueprint, render_template
expenses_bp = Blueprint('expenses', __name__)

# Purchase Summary route (for reports.expenses.purchase_summary endpoint)
@expenses_bp.route('/purchase-summary')
def purchase_summary():
    # TODO: Replace with real data and template
    return render_template('reports/expenses/purchase_summary.html')

# Vendor Aging Report route (for reports.expenses.vendor_aging endpoint)
@expenses_bp.route('/vendor-aging')
def vendor_aging():
    # TODO: Replace with real data and template
    return render_template('reports/expenses/vendor_aging.html')

# Expense Summary route (for reports.expenses.expense_summary endpoint)
@expenses_bp.route('/expense-summary')
def expense_summary():
    # TODO: Replace with real data and template
    return render_template('reports/expenses/expense_summary.html')

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
    from .expenses import expenses_bp # This file will be updated to define expenses_bp
    from .dashboard import reports_dashboard_bp 
    
    # Register sub-blueprints to the main reports_bp
    reports_bp.register_blueprint(tax_bp)
    reports_bp.register_blueprint(sales_bp)
    reports_bp.register_blueprint(financial_bp)
    reports_bp.register_blueprint(expenses_bp) # Register expenses_bp
    reports_bp.register_blueprint(reports_dashboard_bp)
    
    # utils_bp was removed as it's not a Flask Blueprint.

    # Register the main reports_bp with the app
    app.register_blueprint(reports_bp)
