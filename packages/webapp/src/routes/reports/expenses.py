
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
    from datetime import datetime, timedelta
    report_period = {
        'start_date': datetime.now() - timedelta(days=30),
        'end_date': datetime.now()
    }
    return render_template('reports/expenses/expense_summary.html', report_period=report_period)
