# General Ledger route (for reports.financial.general_ledger endpoint)
@financial_bp.route('/general-ledger')
def general_ledger():
    # TODO: Replace with real data and template
    return render_template('reports/financial/general_ledger.html')

from flask import Blueprint, render_template
financial_bp = Blueprint('financial', __name__)

# Cash Flow Statement route (for reports.financial.cash_flow endpoint)
@financial_bp.route('/cash-flow')
def cash_flow():
    # TODO: Replace with real data and template
    return render_template('reports/financial/cash_flow.html')

# Balance Sheet route (for reports.financial.balance_sheet endpoint)
@financial_bp.route('/balance-sheet')
def balance_sheet():
    # TODO: Replace with real data and template
    return render_template('reports/financial/balance_sheet.html')

# Profit & Loss Statement route (for reports.financial.profit_loss endpoint)
@financial_bp.route('/profit-loss')
def profit_loss():
    # TODO: Replace with real data and template
    return render_template('reports/financial/profit_loss.html')

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
