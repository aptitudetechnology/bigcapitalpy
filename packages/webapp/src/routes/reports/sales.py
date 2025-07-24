"""
Sales reports routes for BigCapitalPy.
Handles various sales-related insights.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, and_
# You'll likely need to import models and db here later
# from packages.server.src.models import Invoice, Customer, Item
# from packages.server.src.database import db
# from packages.webapp.src.utils.date_utils import get_date_range # Assuming this utility exists

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/')
@login_required
def index():
    """
    Default sales overview page.
    Could redirect to a common sales report or display a summary.
    """
    # For now, let's redirect to the Sales Summary report as a default
    return redirect(url_for('reports.sales.sales_summary'))

@sales_bp.route('/sales-summary')
@login_required
def sales_summary():
    """
    Sales Summary Report.
    """
    # Placeholder for sales summary data
    summary_data = {
        'total_sales': Decimal('0.00'),
        'sales_by_customer': [],
        'sales_by_item': []
    }
    return render_template('reports/sales_summary.html', summary_data=summary_data)

@sales_bp.route('/customer-aging')
@login_required
def customer_aging():
    """
    Customer Aging Report.
    """
    # Placeholder for customer aging data
    aging_data = {
        'current': Decimal('0.00'),
        '1-30_days': Decimal('0.00'),
        '31-60_days': Decimal('0.00'),
        '61-90_days': Decimal('0.00'),
        'over_90_days': Decimal('0.00'),
        'customers': []
    }
    return render_template('reports/customer_aging.html', aging_data=aging_data)

@sales_bp.route('/invoice-summary')
@login_required
def invoice_summary():
    """
    Invoice Summary Report.
    """
    # Placeholder for invoice summary data
    invoice_data = {
        'total_invoices': 0,
        'paid_invoices': 0,
        'unpaid_invoices': 0,
        'overdue_invoices': 0,
        'invoices': []
    }
    return render_template('reports/invoice_summary.html', invoice_data=invoice_data)

# Add other sales-related routes as needed
