"""
Financial Reports routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, jsonify, make_response, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, extract, and_, or_
from decimal import Decimal
import calendar
import io
import csv

from packages.server.src.models import (
    Account, AccountType, Customer, Vendor, Item, Invoice, InvoiceStatus,
    JournalEntry, JournalLineItem
)
from packages.server.src.database import db

reports_bp = Blueprint('reports', __name__)

def get_date_range(period=None, start_date=None, end_date=None):
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
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = today.replace(day=1)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    
    return start_date, end_date

def calculate_account_balance(account_id, start_date=None, end_date=None):
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

@reports_bp.route('/')
@login_required
def index():
    """Reports dashboard with overview statistics"""
    # Get current year-to-date figures
    today = date.today()
    ytd_start = date(today.year, 1, 1)
    
    # Calculate key metrics
    total_revenue = calculate_income_total(ytd_start, today)
    total_expenses = calculate_expense_total(ytd_start, today)
    net_profit = total_revenue - total_expenses
    accounts_receivable = calculate_accounts_receivable()
    
    report_data = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'accounts_receivable': accounts_receivable
    }
    
    return render_template('reports/index.html', report_data=report_data)

def calculate_income_total(start_date, end_date):
    """Calculate total income for period"""
    income_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.INCOME
    ).all()
    
    total = Decimal('0.00')
    for account in income_accounts:
        # Income accounts have credit balances
        balance = calculate_account_balance(account.id, start_date, end_date)
        total += abs(balance)  # Make positive for display
    
    return total

def calculate_expense_total(start_date, end_date):
    """Calculate total expenses for period"""
    expense_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.EXPENSE
    ).all()
    
    total = Decimal('0.00')
    for account in expense_accounts:
        balance = calculate_account_balance(account.id, start_date, end_date)
        total += balance
    
    return total

def calculate_accounts_receivable():
    """Calculate outstanding accounts receivable"""
    total = db.session.query(func.sum(Invoice.balance)).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE]),
        Invoice.balance > 0
    ).scalar() or Decimal('0.00')
    
    return total

@reports_bp.route('/profit-loss')
@login_required
def profit_loss():
    """Profit & Loss Statement"""
    # Get period parameters
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    export_format = request.args.get('format')
    
    start_date, end_date = get_date_range(period, start_date_str, end_date_str)
    
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
    
    # Calculate balances for each account
    income_data = []
    total_income = Decimal('0.00')
    
    for account in income_accounts:
        balance = calculate_account_balance(account.id, start_date, end_date)
        # Income accounts typically have credit balances, so we reverse the sign for display
        balance = abs(balance)
        income_data.append({
            'id': account.id,
            'name': account.name,
            'code': account.code,
            'balance': balance
        })
        total_income += balance
    
    expense_data = []
    total_expenses = Decimal('0.00')
    
    for account in expense_accounts:
        balance = calculate_account_balance(account.id, start_date, end_date)
        expense_data.append({
            'id': account.id,
            'name': account.name,
            'code': account.code,
            'balance': balance
        })
        total_expenses += balance
    
    # Calculate net profit
    net_profit = total_income - total_expenses
    
    report_data = {
        'income_accounts': income_data,
        'expense_accounts': expense_data,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'gross_profit': total_income,  # Simplified for now
        'cost_of_goods_sold': Decimal('0.00')  # To be implemented
    }
    
    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    # Handle export formats
    if export_format == 'csv':
        return export_profit_loss_csv(report_data, report_period)
    elif export_format == 'pdf':
        # TODO: Implement PDF export
        pass
    elif export_format == 'excel':
        # TODO: Implement Excel export
        pass
    
    return render_template('reports/profit_loss.html', 
                         report_data=report_data, 
                         report_period=report_period)

@reports_bp.route('/balance-sheet')
@login_required
def balance_sheet():
    """Balance Sheet Report"""
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date, end_date = get_date_range(period, start_date_str, end_date_str)
    
    # Get accounts by type
    asset_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        Account.is_active == True
    ).order_by(Account.code).all()
    
    liability_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.LIABILITY,
        Account.is_active == True
    ).order_by(Account.code).all()
    
    equity_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.EQUITY,
        Account.is_active == True
    ).order_by(Account.code).all()
    
    # Calculate balances
    assets_data = []
    total_assets = Decimal('0.00')
    
    for account in asset_accounts:
        balance = calculate_account_balance(account.id, None, end_date)  # Cumulative to date
        assets_data.append({
            'id': account.id,
            'name': account.name,
            'code': account.code,
            'balance': balance
        })
        total_assets += balance
    
    liabilities_data = []
    total_liabilities = Decimal('0.00')
    
    for account in liability_accounts:
        balance = calculate_account_balance(account.id, None, end_date)
        # Liabilities typically have credit balances
        balance = abs(balance)
        liabilities_data.append({
            'id': account.id,
            'name': account.name,
            'code': account.code,
            'balance': balance
        })
        total_liabilities += balance
    
    equity_data = []
    total_equity = Decimal('0.00')
    
    for account in equity_accounts:
        balance = calculate_account_balance(account.id, None, end_date)
        # Equity typically has credit balances
        balance = abs(balance)
        equity_data.append({
            'id': account.id,
            'name': account.name,
            'code': account.code,
            'balance': balance
        })
        total_equity += balance
    
    # Add retained earnings (net profit)
    ytd_start = date(end_date.year, 1, 1)
    retained_earnings = calculate_income_total(ytd_start, end_date) - calculate_expense_total(ytd_start, end_date)
    total_equity += retained_earnings
    
    report_data = {
        'assets': assets_data,
        'liabilities': liabilities_data,
        'equity': equity_data,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'retained_earnings': retained_earnings,
        'total_liabilities_equity': total_liabilities + total_equity
    }
    
    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render_template('reports/balance_sheet.html', 
                         report_data=report_data, 
                         report_period=report_period)

@reports_bp.route('/cash-flow')
@login_required
def cash_flow():
    """Cash Flow Statement"""
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date, end_date = get_date_range(period, start_date_str, end_date_str)
    
    # This is a simplified cash flow statement
    # In a full implementation, you'd need to categorize cash flows properly
    
    # Operating Activities (simplified)
    net_income = calculate_income_total(start_date, end_date) - calculate_expense_total(start_date, end_date)
    
    # Get cash and cash equivalent accounts
    cash_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        Account.name.ilike('%cash%'),
        Account.is_active == True
    ).all()
    
    cash_flow_data = []
    total_cash_change = Decimal('0.00')
    
    for account in cash_accounts:
        opening_balance = calculate_account_balance(account.id, None, start_date - timedelta(days=1))
        closing_balance = calculate_account_balance(account.id, None, end_date)
        change = closing_balance - opening_balance
        
        cash_flow_data.append({
            'account': account.name,
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'change': change
        })
        total_cash_change += change
    
    report_data = {
        'operating_activities': {
            'net_income': net_income,
            'total_operating': net_income  # Simplified
        },
        'investing_activities': {
            'total_investing': Decimal('0.00')  # To be implemented
        },
        'financing_activities': {
            'total_financing': Decimal('0.00')  # To be implemented
        },
        'cash_accounts': cash_flow_data,
        'net_cash_change': total_cash_change
    }
    
    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render_template('reports/cash_flow.html', 
                         report_data=report_data, 
                         report_period=report_period)

@reports_bp.route('/sales-summary')
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

@reports_bp.route('/customer-aging')
@login_required
def customer_aging():
    """Customer Aging Report"""
    # Get all customers with outstanding balances
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
        # Get outstanding invoices for this customer
        invoices = Invoice.query.filter(
            Invoice.customer_id == customer.id,
            Invoice.balance > 0,
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE])
        ).all()
        
        customer_aging = {
            'customer_name': customer.display_name,
            'customer_id': customer.id,
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
            aging_data.append(customer_aging)
    
    # Sort by total outstanding
    aging_data.sort(key=lambda x: x['total'], reverse=True)
    
    report_data = {
        'aging_data': aging_data,
        'totals': totals,
        'report_date': today
    }
    
    return render_template('reports/customer_aging.html', report_data=report_data)

def export_profit_loss_csv(report_data, report_period):
    """Export Profit & Loss report as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Profit & Loss Statement'])
    writer.writerow([f"{report_period['start_date']} to {report_period['end_date']}"])
    writer.writerow([])
    
    # Write income section
    writer.writerow(['INCOME'])
    for account in report_data['income_accounts']:
        writer.writerow([account['name'], str(account['balance'])])
    writer.writerow(['Total Income', str(report_data['total_income'])])
    writer.writerow([])
    
    # Write expense section
    writer.writerow(['EXPENSES'])
    for account in report_data['expense_accounts']:
        writer.writerow([account['name'], str(account['balance'])])
    writer.writerow(['Total Expenses', str(report_data['total_expenses'])])
    writer.writerow([])
    
    # Write net profit
    writer.writerow(['Net Profit', str(report_data['net_profit'])])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=profit_loss.csv'
    
    return response

@reports_bp.route('/expense-summary')
@login_required
def expense_summary():
    """Expense Summary Report - Coming Soon"""
    return render_template('reports/expense_summary.html')

@reports_bp.route('/vendor-aging')
@login_required
def vendor_aging():
    """Vendor Aging Report - Coming Soon"""
    return render_template('reports/vendor_aging.html')

@reports_bp.route('/invoice-summary')
@login_required
def invoice_summary():
    """Invoice Summary Report - Coming Soon"""
    return render_template('reports/invoice_summary.html')

@reports_bp.route('/purchase-summary')
@login_required
def purchase_summary():
    """Purchase Summary Report - Coming Soon"""
    return render_template('reports/purchase_summary.html')
