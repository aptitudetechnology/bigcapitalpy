"""
Sales reports routes for BigCapitalPy.
Handles various sales-related insights.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from packages.server.src.models import db, Invoice, Customer, InvoiceStatus
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
    return render_template('reports/customer-sales/sales_summary.html', summary_data=summary_data)

@sales_bp.route('/customer-aging')
@login_required
def customer_aging():
    """
    Customer Aging Report.
    """
    today = date.today()
    as_of_date = request.args.get('as_of_date')
    if as_of_date:
        try:
            as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
        except Exception:
            as_of_date = today
    else:
        as_of_date = today

    # Query all open (unpaid) invoices as of the date
    invoices = (
        db.session.query(Invoice, Customer)
        .join(Customer, Invoice.customer_id == Customer.id)
        .filter(Invoice.balance > 0)
        .filter(Invoice.due_date <= as_of_date)
        .all()
    )

    # Prepare aging buckets
    buckets = {
        'current': 0.0,
        '1_30': 0.0,
        '31_60': 0.0,
        '61_90': 0.0,
        'over_90': 0.0,
        'total': 0.0
    }
    aging_data = []
    customer_map = {}
    for invoice, customer in invoices:
        days_past_due = (as_of_date - invoice.due_date).days
        amt = float(invoice.balance)
        # Assign to bucket
        if days_past_due <= 0:
            bucket = 'current'
        elif days_past_due <= 30:
            bucket = '1_30'
        elif days_past_due <= 60:
            bucket = '31_60'
        elif days_past_due <= 90:
            bucket = '61_90'
        else:
            bucket = 'over_90'

        # Group by customer
        cid = customer.id
        if cid not in customer_map:
            customer_map[cid] = {
                'customer_id': cid,
                'customer_name': customer.display_name,
                'current': 0.0,
                '1_30': 0.0,
                '31_60': 0.0,
                '61_90': 0.0,
                'over_90': 0.0,
                'total': 0.0
            }
        customer_map[cid][bucket] += amt
        customer_map[cid]['total'] += amt
        buckets[bucket] += amt
        buckets['total'] += amt

    aging_data = list(customer_map.values())

    report_data = {
        'as_of_date': as_of_date,
        'report_date': as_of_date,
        'aging_data': aging_data,
        'totals': buckets
    }
    # If no data, ensure template gets zeros/empty lists
    if not aging_data:
        report_data['aging_data'] = []
        report_data['totals'] = {
            'current': 0.0,
            '1_30': 0.0,
            '31_60': 0.0,
            '61_90': 0.0,
            'over_90': 0.0,
            'total': 0.0
        }
    return render_template('reports/customer-sales/customer_aging.html', report_data=report_data)

@sales_bp.route('/invoice-summary')
@login_required
def invoice_summary():
    """
    Invoice Summary Report (database-driven).
    """
    today = date.today()
    # Query all invoices for the current organization (if multi-tenant)
    invoices = db.session.query(Invoice).all()
    total_invoices = len(invoices)
    paid_invoices = 0
    unpaid_invoices = 0
    overdue_invoices = 0
    invoice_list = []
    for inv in invoices:
        status = inv.status.name if hasattr(inv.status, 'name') else str(inv.status)
        is_paid = status == 'PAID'
        is_overdue = (status != 'PAID' and inv.due_date < today and float(inv.balance) > 0)
        if is_paid:
            paid_invoices += 1
        else:
            unpaid_invoices += 1
        if is_overdue:
            overdue_invoices += 1
        invoice_list.append({
            'id': inv.id,
            'invoice_number': inv.invoice_number,
            'customer_id': inv.customer_id,
            'due_date': inv.due_date,
            'status': status,
            'total': float(inv.total),
            'paid_amount': float(inv.paid_amount),
            'balance': float(inv.balance)
        })
    invoice_data = {
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'overdue_invoices': overdue_invoices,
        'invoices': invoice_list
    }
    return render_template('reports/customer-sales/invoice_summary.html', invoice_data=invoice_data)

# Add other sales-related routes as needed
