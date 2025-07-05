"""
Reports API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from decimal import Decimal
import calendar

from packages.server.src.models import (
    Account, AccountType, Customer, Invoice, InvoiceStatus,
    JournalEntry, JournalLineItem
)
from packages.server.src.database import db
from ..utils import api_response, api_error, require_api_key, serialize_model

reports_api_bp = Blueprint('reports_api', __name__)

def get_date_range_api(period=None, start_date=None, end_date=None):
    """Get date range based on period or custom dates"""
    today = date.today()
    
    if period == 'this_month':
        start_date = today.replace(day=1)
        end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    elif period == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1)
        end_date = last_month.replace(day=calendar.monthrange(last_month.year, last_month.month)[1])
    elif period == 'this_quarter':
        quarter = (today.month - 1) // 3 + 1
        start_date = date(today.year, 3 * quarter - 2, 1)
        end_date = date(today.year, 3 * quarter, calendar.monthrange(today.year, 3 * quarter)[1])
    elif period == 'last_quarter':
        quarter = (today.month - 1) // 3 + 1
        if quarter == 1:
            quarter = 4
            year = today.year - 1
        else:
            quarter -= 1
            year = today.year
        start_date = date(year, 3 * quarter - 2, 1)
        end_date = date(year, 3 * quarter, calendar.monthrange(year, 3 * quarter)[1])
    elif period == 'this_year':
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 12, 31)
    elif period == 'last_year':
        start_date = date(today.year - 1, 1, 1)
        end_date = date(today.year - 1, 12, 31)
    else:
        # Custom period or default to current month
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = today.replace(day=1)
        
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    
    return start_date, end_date

def calculate_account_balance_api(account_id, start_date=None, end_date=None):
    """Calculate account balance for a given period"""
    query = db.session.query(func.sum(JournalLineItem.debit - JournalLineItem.credit)).filter(
        JournalLineItem.account_id == account_id
    ).join(JournalEntry).filter(
        JournalEntry.organization_id == current_user.organization_id
    )
    
    if start_date:
        query = query.filter(JournalEntry.date >= start_date)
    if end_date:
        query = query.filter(JournalEntry.date <= end_date)
    
    balance = query.scalar() or Decimal('0.00')
    return balance

@reports_api_bp.route('/profit-loss', methods=['GET'])
@require_api_key
def profit_loss_report():
    """Generate Profit & Loss report"""
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date, end_date = get_date_range_api(period, start_date_str, end_date_str)
    
    # Get income accounts
    income_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.INCOME,
        Account.is_active == True
    ).order_by(Account.code).all()
    
    # Get expense accounts
    expense_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.EXPENSE,
        Account.is_active == True
    ).order_by(Account.code).all()
    
    # Calculate balances
    income_data = []
    total_income = Decimal('0.00')
    
    for account in income_accounts:
        balance = calculate_account_balance_api(account.id, start_date, end_date)
        balance = abs(balance)  # Income accounts have credit balances
        income_data.append({
            'id': account.id,
            'name': account.name,
            'code': account.code,
            'balance': float(balance)
        })
        total_income += balance
    
    expense_data = []
    total_expenses = Decimal('0.00')
    
    for account in expense_accounts:
        balance = calculate_account_balance_api(account.id, start_date, end_date)
        expense_data.append({
            'id': account.id,
            'name': account.name,
            'code': account.code,
            'balance': float(balance)
        })
        total_expenses += balance
    
    net_profit = total_income - total_expenses
    
    report_data = {
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'income': {
            'accounts': income_data,
            'total': float(total_income)
        },
        'expenses': {
            'accounts': expense_data,
            'total': float(total_expenses)
        },
        'net_profit': float(net_profit)
    }
    
    return api_response(data={'report': report_data})

@reports_api_bp.route('/balance-sheet', methods=['GET'])
@require_api_key
def balance_sheet_report():
    """Generate Balance Sheet report"""
    end_date_str = request.args.get('end_date')
    period = request.args.get('period', 'this_month')
    
    _, end_date = get_date_range_api(period, None, end_date_str)
    
    # Get accounts by type
    account_types = [AccountType.ASSET, AccountType.LIABILITY, AccountType.EQUITY]
    report_data = {
        'as_of_date': end_date.isoformat(),
        'assets': {'accounts': [], 'total': 0.0},
        'liabilities': {'accounts': [], 'total': 0.0},
        'equity': {'accounts': [], 'total': 0.0}
    }
    
    for account_type in account_types:
        accounts = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == account_type,
            Account.is_active == True
        ).order_by(Account.code).all()
        
        accounts_data = []
        total_balance = Decimal('0.00')
        
        for account in accounts:
            balance = calculate_account_balance_api(account.id, None, end_date)
            
            # Liabilities and equity typically have credit balances
            if account_type in [AccountType.LIABILITY, AccountType.EQUITY]:
                balance = abs(balance)
            
            accounts_data.append({
                'id': account.id,
                'name': account.name,
                'code': account.code,
                'balance': float(balance)
            })
            total_balance += balance
        
        section_name = account_type.value + 's' if account_type != AccountType.EQUITY else 'equity'
        report_data[section_name]['accounts'] = accounts_data
        report_data[section_name]['total'] = float(total_balance)
    
    # Add retained earnings to equity
    ytd_start = date(end_date.year, 1, 1)
    income_total = sum(
        abs(calculate_account_balance_api(acc.id, ytd_start, end_date))
        for acc in Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.INCOME,
            Account.is_active == True
        ).all()
    )
    
    expense_total = sum(
        calculate_account_balance_api(acc.id, ytd_start, end_date)
        for acc in Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.EXPENSE,
            Account.is_active == True
        ).all()
    )
    
    retained_earnings = float(income_total - expense_total)
    report_data['equity']['total'] += retained_earnings
    report_data['retained_earnings'] = retained_earnings
    
    # Calculate totals
    report_data['total_assets'] = report_data['assets']['total']
    report_data['total_liabilities_equity'] = (
        report_data['liabilities']['total'] + report_data['equity']['total']
    )
    
    return api_response(data={'report': report_data})

@reports_api_bp.route('/sales-summary', methods=['GET'])
@require_api_key
def sales_summary_report():
    """Generate Sales Summary report"""
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date, end_date = get_date_range_api(period, start_date_str, end_date_str)
    
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
        customer_id = invoice.customer.id
        customer_name = invoice.customer.display_name
        
        if customer_id not in customer_sales:
            customer_sales[customer_id] = {
                'customer_id': customer_id,
                'customer_name': customer_name,
                'total_invoiced': Decimal('0.00'),
                'total_paid': Decimal('0.00'),
                'outstanding': Decimal('0.00'),
                'invoice_count': 0
            }
        
        customer_sales[customer_id]['total_invoiced'] += invoice.total
        customer_sales[customer_id]['total_paid'] += invoice.paid_amount
        customer_sales[customer_id]['outstanding'] += invoice.balance
        customer_sales[customer_id]['invoice_count'] += 1
        
        total_sales += invoice.total
        total_paid += invoice.paid_amount
        total_outstanding += invoice.balance
    
    # Convert to list and format
    sales_data = []
    for data in customer_sales.values():
        sales_data.append({
            'customer_id': data['customer_id'],
            'customer_name': data['customer_name'],
            'total_invoiced': float(data['total_invoiced']),
            'total_paid': float(data['total_paid']),
            'outstanding': float(data['outstanding']),
            'invoice_count': data['invoice_count']
        })
    
    # Sort by total sales
    sales_data.sort(key=lambda x: x['total_invoiced'], reverse=True)
    
    report_data = {
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'summary': {
            'total_sales': float(total_sales),
            'total_paid': float(total_paid),
            'total_outstanding': float(total_outstanding),
            'invoice_count': len(invoices)
        },
        'sales_by_customer': sales_data
    }
    
    return api_response(data={'report': report_data})

@reports_api_bp.route('/customer-aging', methods=['GET'])
@require_api_key
def customer_aging_report():
    """Generate Customer Aging report"""
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.current_balance > 0
    ).all()
    
    aging_data = []
    totals = {
        'current': Decimal('0.00'),
        '1_30': Decimal('0.00'),
        '31_60': Decimal('0.00'),
        '61_90': Decimal('0.00'),
        'over_90': Decimal('0.00'),
        'total': Decimal('0.00')
    }
    
    today = date.today()
    
    for customer in customers:
        invoices = Invoice.query.filter(
            Invoice.customer_id == customer.id,
            Invoice.balance > 0,
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE])
        ).all()
        
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
        
        for invoice in invoices:
            days_overdue = (today - invoice.due_date).days
            amount = invoice.balance
            
            if days_overdue <= 0:
                customer_aging['current'] += amount
                totals['current'] += amount
            elif days_overdue <= 30:
                customer_aging['1_30'] += amount
                totals['1_30'] += amount
            elif days_overdue <= 60:
                customer_aging['31_60'] += amount
                totals['31_60'] += amount
            elif days_overdue <= 90:
                customer_aging['61_90'] += amount
                totals['61_90'] += amount
            else:
                customer_aging['over_90'] += amount
                totals['over_90'] += amount
            
            customer_aging['total'] += amount
            totals['total'] += amount
        
        if customer_aging['total'] > 0:
            # Convert to float for JSON serialization
            for key in customer_aging:
                if isinstance(customer_aging[key], Decimal):
                    customer_aging[key] = float(customer_aging[key])
            aging_data.append(customer_aging)
    
    # Sort by total outstanding
    aging_data.sort(key=lambda x: x['total'], reverse=True)
    
    # Convert totals to float
    totals_float = {key: float(value) for key, value in totals.items()}
    
    report_data = {
        'as_of_date': today.isoformat(),
        'totals': totals_float,
        'aging_data': aging_data
    }
    
    return api_response(data={'report': report_data})

@reports_api_bp.route('/dashboard-metrics', methods=['GET'])
@require_api_key
def dashboard_metrics():
    """Get dashboard metrics for API consumption"""
    org_id = current_user.organization_id
    today = date.today()
    
    # Current month metrics
    month_start = today.replace(day=1)
    
    # This month's sales
    monthly_sales = db.session.query(func.sum(Invoice.total)).filter(
        Invoice.organization_id == org_id,
        Invoice.invoice_date >= month_start,
        Invoice.status != InvoiceStatus.CANCELLED
    ).scalar() or 0
    
    # Outstanding receivables
    outstanding = db.session.query(func.sum(Invoice.balance)).filter(
        Invoice.organization_id == org_id,
        Invoice.balance > 0,
        Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE])
    ).scalar() or 0
    
    # Invoice counts by status
    invoice_counts = {}
    for status in InvoiceStatus:
        count = Invoice.query.filter_by(
            organization_id=org_id,
            status=status
        ).count()
        invoice_counts[status.value] = count
    
    # Monthly sales trend (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_trends = db.session.query(
        func.date_trunc('month', Invoice.invoice_date).label('month'),
        func.sum(Invoice.total).label('total')
    ).filter(
        Invoice.organization_id == org_id,
        Invoice.invoice_date >= six_months_ago,
        Invoice.status != InvoiceStatus.CANCELLED
    ).group_by('month').order_by('month').all()
    
    trends_data = []
    for trend in monthly_trends:
        trends_data.append({
            'month': trend.month.strftime('%Y-%m'),
            'total': float(trend.total or 0)
        })
    
    metrics = {
        'monthly_sales': float(monthly_sales),
        'outstanding_receivables': float(outstanding),
        'invoice_counts': invoice_counts,
        'monthly_trends': trends_data,
        'generated_at': datetime.utcnow().isoformat()
    }
    
    return api_response(data={'metrics': metrics})
