"""
Sales & Customer Reports module for BigCapitalPy
Contains Sales Summary, Invoice Summary, and Customer Aging reports
"""

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import func

from packages.server.src.models import (
    Customer, Invoice, InvoiceStatus
)
from packages.server.src.database import db
# Old import path commented out: from .utils import get_date_range
# New import path for get_date_range from the more general utils directory
from packages.webapp.src.utils.date_utils import get_date_range

sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/sales-summary')
@login_required
def sales_summary():
    """Sales Summary Report"""
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date, end_date = get_date_range(period, start_date_str, end_date_str)
    
    # Get sales data from invoices
    invoices = Invoice.query.filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date,
        Invoice.status != InvoiceStatus.CANCELLED
    ).all()
    
    # Group by customer
    customer_sales = {}
    total_sales = Decimal('0.00')
    total_paid = Decimal('0.00')
    total_outstanding = Decimal('0.00')
    
    for invoice in invoices:
        customer_name = invoice.customer.display_name
        if customer_name not in customer_sales:
            customer_sales[customer_name] = {
                'customer_id': invoice.customer.id,
                'total_invoiced': Decimal('0.00'),
                'total_paid': Decimal('0.00'),
                'outstanding': Decimal('0.00'),
                'invoice_count': 0
            }
        
        customer_sales[customer_name]['total_invoiced'] += invoice.total
        customer_sales[customer_name]['total_paid'] += invoice.paid_amount
        customer_sales[customer_name]['outstanding'] += invoice.balance
        customer_sales[customer_name]['invoice_count'] += 1
        
        total_sales += invoice.total
        total_paid += invoice.paid_amount
        total_outstanding += invoice.balance
    
    # Convert to list and sort by total sales
    sales_data = []
    for customer_name, data in customer_sales.items():
        sales_data.append({
            'customer_name': customer_name,
            **data
        })
    sales_data.sort(key=lambda x: x['total_invoiced'], reverse=True)
    
    report_data = {
        'sales_by_customer': sales_data,
        'total_sales': total_sales,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        'invoice_count': len(invoices)
    }
    
    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render_template('reports/sales_summary.html', 
                         report_data=report_data, 
                         report_period=report_period)


@sales_bp.route('/invoice-summary')
@login_required
def invoice_summary():
    """Invoice Summary Report"""
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    status_filter = request.args.get('status', 'all')
    
    start_date, end_date = get_date_range(period, start_date_str, end_date_str)
    
    # Build query
    query = Invoice.query.filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date
    )
    
    if status_filter != 'all':
        query = query.filter(Invoice.status == InvoiceStatus(status_filter))
    
    invoices = query.order_by(Invoice.invoice_date.desc()).all()
    
    # Calculate summary statistics
    total_invoiced = sum(invoice.total for invoice in invoices)
    total_paid = sum(invoice.paid_amount for invoice in invoices)
    total_outstanding = sum(invoice.balance for invoice in invoices)
    
    # Group by status
    status_summary = {}
    for status in InvoiceStatus:
        status_invoices = [inv for inv in invoices if inv.status == status]
        status_summary[status.value] = {
            'count': len(status_invoices),
            'total_amount': sum(inv.total for inv in status_invoices),
            'percentage': (len(status_invoices) / len(invoices) * 100) if invoices else 0
        }
    
    # Group by customer
    customer_summary = {}
    for invoice in invoices:
        customer_name = invoice.customer.display_name
        if customer_name not in customer_summary:
            customer_summary[customer_name] = {
                'customer_id': invoice.customer.id,
                'invoice_count': 0,
                'total_amount': Decimal('0.00'),
                'paid_amount': Decimal('0.00'),
                'outstanding': Decimal('0.00')
            }
        
        customer_summary[customer_name]['invoice_count'] += 1
        customer_summary[customer_name]['total_amount'] += invoice.total
        customer_summary[customer_name]['paid_amount'] += invoice.paid_amount
        customer_summary[customer_name]['outstanding'] += invoice.balance
    
    # Convert to sorted list
    customer_data = []
    for customer_name, data in customer_summary.items():
        customer_data.append({
            'customer_name': customer_name,
            **data
        })
    customer_data.sort(key=lambda x: x['total_amount'], reverse=True)
    
    report_data = {
        'invoices': invoices,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        'status_summary': status_summary,
        'customer_summary': customer_data,
        'invoice_count': len(invoices)
    }
    
    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render_template('reports/invoice_summary.html', 
                         report_data=report_data, 
                         report_period=report_period)


@sales_bp.route('/customer-aging')
@login_required
def customer_aging():
    """Customer Aging Report"""
    as_of_date = request.args.get('as_of_date')
    if as_of_date:
        as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
    else:
        as_of_date = date.today()
    
    # Get all customers with outstanding balances
    customers_with_balances = db.session.query(Customer).join(Invoice).filter(
        Customer.organization_id == current_user.organization_id,
        Invoice.balance > 0,
        Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE])
    ).distinct().all()
    
    aging_data = []
    totals = {
        'current': Decimal('0.00'),
        '1_30': Decimal('0.00'),
        '31_60': Decimal('0.00'),
        '61_90': Decimal('0.00'),
        'over_90': Decimal('0.00'),
        'total': Decimal('0.00')
    }
    
    for customer in customers_with_balances:
        customer_aging = {
            'customer_id': customer.id,
            'customer_name': customer.display_name,
            'current': Decimal('0.00'),
            '1_30': Decimal('0.00'),
            '31_60': Decimal('0.00'),
            '61_90': Decimal('0.00'),
            'over_90': Decimal('0.00'),
            'total': Decimal('0.00')
        }
        
        # Get outstanding invoices for this customer
        outstanding_invoices = Invoice.query.filter(
            Invoice.customer_id == customer.id,
            Invoice.organization_id == current_user.organization_id,
            Invoice.balance > 0,
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE])
        ).all()
        
        for invoice in outstanding_invoices:
            days_past_due = (as_of_date - invoice.due_date).days if invoice.due_date else 0
            
            if days_past_due <= 0:
                customer_aging['current'] += invoice.balance
            elif 1 <= days_past_due <= 30:
                customer_aging['1_30'] += invoice.balance
            elif 31 <= days_past_due <= 60:
                customer_aging['31_60'] += invoice.balance
            elif 61 <= days_past_due <= 90:
                customer_aging['61_90'] += invoice.balance
            else:
                customer_aging['over_90'] += invoice.balance
            
            customer_aging['total'] += invoice.balance
        
        if customer_aging['total'] > 0:
            aging_data.append(customer_aging)
            
            totals['current'] += customer_aging['current']
            totals['1_30'] += customer_aging['1_30']
            totals['31_60'] += customer_aging['31_60']
            totals['61_90'] += customer_aging['61_90']
            totals['over_90'] += customer_aging['over_90']
            totals['total'] += customer_aging['total']
            
    # Sort by customer name
    aging_data.sort(key=lambda x: x['customer_name'])
    
    report_data = {
        'aging_data': aging_data,
        'totals': totals,
        'as_of_date': as_of_date
    }
    
    return render_template('reports/customer_aging.html', 
                         report_data=report_data)
