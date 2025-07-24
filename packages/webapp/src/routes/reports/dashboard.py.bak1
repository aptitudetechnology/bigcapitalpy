"""
Reports Dashboard blueprint for BigCapitalPy.
Contains the main index page for all financial reports.
"""

from flask import Blueprint, render_template, request
from flask_login import login_required # Assuming reports dashboard requires login
from decimal import Decimal # Needed for placeholder data

# Define the reports dashboard blueprint
# This blueprint will contain the 'index' route for the /reports URL prefix
reports_dashboard_bp = Blueprint('reports_dashboard', __name__)

@reports_dashboard_bp.route('/')
@login_required 
def index():
    """
    Main index route for the /reports URL prefix.
    This serves as the reports dashboard, displaying an overview and links.
    """
    # Provide placeholder or empty report_data dictionary for the template
    # In a real application, you would fetch actual summary data here.
    report_data = {
        'total_revenue': Decimal('0.00'),
        'total_expenses': Decimal('0.00'),
        'net_profit': Decimal('0.00'),
        'total_sales_invoices': 0,
        'total_purchase_bills': 0,
        'cash_balance': Decimal('0.00'),
        'unreconciled_transactions': 0,
        'accounts_receivable': Decimal('0.00')
    }

    # You might also want to fetch some recent reports data here
    recent_reports = [] # Placeholder for now

    return render_template('reports/index.html', 
                           report_data=report_data,
                           recent_reports=recent_reports)

# You can add other reports-specific dashboard routes here if needed
