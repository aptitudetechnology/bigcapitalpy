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
    JournalEntry, JournalLineItem, TaxCode, TaxType, BASReport
)
from packages.server.src.database import db

reports_bp = Blueprint('reports', __name__)
@reports_bp.route('/custom')
@login_required
def custom():
    """Custom Report Builder (Placeholder)"""
    return render_template('reports/custom.html')

@reports_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard (Placeholder)"""
    return render_template('dashboard.html')

@reports_bp.route('/profitability')
@login_required
def profitability():
    """Profitability Report (Placeholder)"""
    return render_template('reports/profitability.html')


@reports_bp.route('/tax-summary')
@login_required
def tax_summary():
    """Tax Summary Report (Placeholder)"""
    return render_template('reports/tax_summary.html')

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

@reports_bp.route('/customer-aging')
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
            Invoice.balance > 0,
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE])
        ).all()
        
        for invoice in outstanding_invoices:
            days_old = (as_of_date - invoice.invoice_date).days
            balance = invoice.balance
            
            if days_old <= 0:
                customer_aging['current'] += balance
                totals['current'] += balance
            elif days_old <= 30:
                customer_aging['1_30'] += balance
                totals['1_30'] += balance
            elif days_old <= 60:
                customer_aging['31_60'] += balance
                totals['31_60'] += balance
            elif days_old <= 90:
                customer_aging['61_90'] += balance
                totals['61_90'] += balance
            else:
                customer_aging['over_90'] += balance
                totals['over_90'] += balance
            
            customer_aging['total'] += balance
            totals['total'] += balance
        
        if customer_aging['total'] > 0:
            aging_data.append(customer_aging)
    
    # Sort by total outstanding (descending)
    aging_data.sort(key=lambda x: x['total'], reverse=True)
    
    report_data = {
        'aging_data': aging_data,
        'totals': totals,
        'as_of_date': as_of_date
    }
    
    return render_template('reports/customer_aging.html', report_data=report_data)

@reports_bp.route('/vendor-aging')
@login_required
def vendor_aging():
    """Vendor Aging Report"""
    as_of_date = request.args.get('as_of_date')
    if as_of_date:
        as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
    else:
        as_of_date = date.today()
    
    # Get all vendors (for future purchase orders/bills implementation)
    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.is_active == True
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
    
    # For now, this is a placeholder since we don't have bills/purchase orders yet
    # In a full implementation, you'd calculate aging based on unpaid bills
    
    report_data = {
        'aging_data': aging_data,
        'totals': totals,
        'as_of_date': as_of_date,
        'vendors': vendors
    }
    
    return render_template('reports/vendor_aging.html', report_data=report_data)

@reports_bp.route('/expense-summary')
@login_required
def expense_summary():
    """Expense Summary Report"""
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date, end_date = get_date_range(period, start_date_str, end_date_str)
    
    # Get expense accounts
    expense_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.EXPENSE,
        Account.is_active == True
    ).order_by(Account.code).all()
    
    expense_data = []
    total_expenses = Decimal('0.00')
    
    for account in expense_accounts:
        current_period = calculate_account_balance(account.id, start_date, end_date)
        
        # Calculate year-to-date
        ytd_start = date(end_date.year, 1, 1)
        ytd_balance = calculate_account_balance(account.id, ytd_start, end_date)
        
        # Calculate previous period for comparison
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length + 1)
        prev_end = start_date - timedelta(days=1)
        previous_period = calculate_account_balance(account.id, prev_start, prev_end)
        
        # Calculate percentage change
        if previous_period != 0:
            percent_change = ((current_period - previous_period) / abs(previous_period)) * 100
        else:
            percent_change = 100 if current_period > 0 else 0
        
        expense_data.append({
            'id': account.id,
            'name': account.name,
            'code': account.code,
            'current_period': current_period,
            'previous_period': previous_period,
            'ytd_balance': ytd_balance,
            'percent_change': percent_change
        })
        
        total_expenses += current_period
    
    # Sort by current period amount (descending)
    expense_data.sort(key=lambda x: x['current_period'], reverse=True)
    
    report_data = {
        'expense_accounts': expense_data,
        'total_expenses': total_expenses,
        'period_comparison': {
            'current_start': start_date,
            'current_end': end_date,
            'previous_start': prev_start,
            'previous_end': prev_end
        }
    }
    
    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render_template('reports/expense_summary.html', 
                         report_data=report_data, 
                         report_period=report_period)

@reports_bp.route('/invoice-summary')
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

@reports_bp.route('/purchase-summary')
@login_required
def purchase_summary():
    """Purchase Summary Report - Placeholder for future purchase orders"""
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date, end_date = get_date_range(period, start_date_str, end_date_str)
    
    # For now, show expense account activity as a proxy for purchases
    expense_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.EXPENSE,
        Account.is_active == True
    ).order_by(Account.code).all()
    
    purchase_data = []
    total_purchases = Decimal('0.00')
    
    for account in expense_accounts:
        balance = calculate_account_balance(account.id, start_date, end_date)
        if balance > 0:
            purchase_data.append({
                'account_name': account.name,
                'account_code': account.code,
                'amount': balance
            })
            total_purchases += balance
    
    # Sort by amount
    purchase_data.sort(key=lambda x: x['amount'], reverse=True)
    
    report_data = {
        'purchase_data': purchase_data,
        'total_purchases': total_purchases
    }
    
    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render_template('reports/purchase_summary.html', 
                         report_data=report_data, 
                         report_period=report_period)

# Add new comprehensive reports

@reports_bp.route('/trial-balance')
@login_required
def trial_balance():
    """Trial Balance Report"""
    as_of_date = request.args.get('as_of_date')
    if as_of_date:
        as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
    else:
        as_of_date = date.today()
    
    # Get all accounts
    accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.is_active == True
    ).order_by(Account.code).all()
    
    trial_balance_data = []
    total_debits = Decimal('0.00')
    total_credits = Decimal('0.00')
    
    for account in accounts:
        balance = calculate_account_balance(account.id, None, as_of_date)
        
        # Determine if balance should be shown as debit or credit
        if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
            # Normal debit balance accounts
            if balance >= 0:
                debit_balance = balance
                credit_balance = Decimal('0.00')
            else:
                debit_balance = Decimal('0.00')
                credit_balance = abs(balance)
        else:
            # Normal credit balance accounts (LIABILITY, EQUITY, INCOME)
            if balance <= 0:
                debit_balance = Decimal('0.00')
                credit_balance = abs(balance)
            else:
                debit_balance = balance
                credit_balance = Decimal('0.00')
        
        trial_balance_data.append({
            'account_code': account.code,
            'account_name': account.name,
            'account_type': account.type.value,
            'debit_balance': debit_balance,
            'credit_balance': credit_balance
        })
        
        total_debits += debit_balance
        total_credits += credit_balance
    
    report_data = {
        'trial_balance_data': trial_balance_data,
        'total_debits': total_debits,
        'total_credits': total_credits,
        'is_balanced': total_debits == total_credits,
        'as_of_date': as_of_date
    }
    
    return render_template('reports/trial_balance.html', report_data=report_data)

@reports_bp.route('/general-ledger')
@login_required
def general_ledger():
    """General Ledger Report"""
    account_id = request.args.get('account_id')
    period = request.args.get('period', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date, end_date = get_date_range(period, start_date_str, end_date_str)
    
    if account_id:
        account = Account.query.filter(
            Account.id == account_id,
            Account.organization_id == current_user.organization_id
        ).first_or_404()
        
        # Get journal line items for this account
        line_items = db.session.query(JournalLineItem).join(JournalEntry).filter(
            JournalLineItem.account_id == account_id,
            JournalEntry.organization_id == current_user.organization_id,
            JournalEntry.date >= start_date,
            JournalEntry.date <= end_date
        ).order_by(JournalEntry.date, JournalEntry.id).all()
        
        # Calculate running balance
        opening_balance = calculate_account_balance(account_id, None, start_date - timedelta(days=1))
        running_balance = opening_balance
        
        ledger_entries = []
        for item in line_items:
            if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
                # Normal debit balance accounts
                running_balance += (item.debit or 0) - (item.credit or 0)
            else:
                # Normal credit balance accounts
                running_balance += (item.credit or 0) - (item.debit or 0)
            
            ledger_entries.append({
                'date': item.journal_entry.date,
                'entry_number': item.journal_entry.entry_number,
                'description': item.description or item.journal_entry.description,
                'reference': item.journal_entry.reference,
                'debit': item.debit,
                'credit': item.credit,
                'balance': running_balance
            })
        
        report_data = {
            'account': account,
            'ledger_entries': ledger_entries,
            'opening_balance': opening_balance,
            'closing_balance': running_balance
        }
    else:
        # Show account selection
        accounts = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.is_active == True
        ).order_by(Account.code).all()
        
        report_data = {
            'accounts': accounts,
            'account': None
        }
    
    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render_template('reports/general_ledger.html', 
                         report_data=report_data, 
                         report_period=report_period)

class AustralianGSTBASReport:
    """
    Australian GST Business Activity Statement (BAS) Report Generator
    Calculates all required GST fields for ATO submission
    """
    
    def __init__(self, start_date, end_date, organization_id):
        self.start_date = start_date if isinstance(start_date, date) else datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = end_date if isinstance(end_date, date) else datetime.strptime(end_date, '%Y-%m-%d').date()
        self.organization_id = organization_id
        
        # Validate quarter alignment
        self.quarter = self._get_quarter()
        
        # GST rate constants
        self.GST_RATE = Decimal('0.10')  # 10% GST
        self.GST_DIVISOR = Decimal('11')  # 1 + GST rate for inclusive calculations
        
    def _get_quarter(self):
        """Get the BAS quarter from the end date"""
        month = self.end_date.month
        year = self.end_date.year
        
        if month in [1, 2, 3]:
            return f"{year}-Q1"
        elif month in [4, 5, 6]:
            return f"{year}-Q2"
        elif month in [7, 8, 9]:
            return f"{year}-Q3"
        else:
            return f"{year}-Q4"
    
    def _get_tax_codes_for_type(self, tax_type):
        """Get tax codes for a specific tax type"""
        return TaxCode.query.filter_by(
            organization_id=self.organization_id,
            tax_type=tax_type,
            is_active=True
        ).all()
    
    def calculate_g1(self):
        """
        G1 - Total Sales (GST Inclusive)
        Include all sales with GST
        """
        gst_tax_codes = self._get_tax_codes_for_type(TaxType.GST_STANDARD)
        tax_code_ids = [tc.id for tc in gst_tax_codes]
        
        # Get sales from invoices with GST
        invoice_total = db.session.query(func.sum(Invoice.total)).filter(
            Invoice.organization_id == self.organization_id,
            Invoice.invoice_date.between(self.start_date, self.end_date),
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PAID]),
            Invoice.line_items.any(InvoiceLineItem.tax_code_id.in_(tax_code_ids))
        ).scalar() or Decimal('0')
        
        # Get sales from journal entries with GST
        journal_sales = db.session.query(func.sum(JournalLineItem.credit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.REVENUE,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(invoice_total + journal_sales, 2)
    
    def calculate_g2(self):
        """
        G2 - Export Sales
        GST-free export sales
        """
        export_tax_codes = self._get_tax_codes_for_type(TaxType.EXPORT)
        tax_code_ids = [tc.id for tc in export_tax_codes]
        
        # Get export sales from invoices
        invoice_exports = db.session.query(func.sum(Invoice.total)).filter(
            Invoice.organization_id == self.organization_id,
            Invoice.invoice_date.between(self.start_date, self.end_date),
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PAID]),
            Invoice.line_items.any(InvoiceLineItem.tax_code_id.in_(tax_code_ids))
        ).scalar() or Decimal('0')
        
        # Get export sales from journal entries
        journal_exports = db.session.query(func.sum(JournalLineItem.credit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.REVENUE,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(invoice_exports + journal_exports, 2)
    
    def calculate_g3(self):
        """
        G3 - Other GST-Free Sales
        Domestic GST-free sales (excluding exports)
        """
        gst_free_tax_codes = self._get_tax_codes_for_type(TaxType.GST_FREE)
        tax_code_ids = [tc.id for tc in gst_free_tax_codes]
        
        # Get GST-free sales from invoices
        invoice_gst_free = db.session.query(func.sum(Invoice.total)).filter(
            Invoice.organization_id == self.organization_id,
            Invoice.invoice_date.between(self.start_date, self.end_date),
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PAID]),
            Invoice.line_items.any(InvoiceLineItem.tax_code_id.in_(tax_code_ids))
        ).scalar() or Decimal('0')
        
        # Get GST-free sales from journal entries
        journal_gst_free = db.session.query(func.sum(JournalLineItem.credit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.REVENUE,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(invoice_gst_free + journal_gst_free, 2)
    
    def calculate_g4(self):
        """
        G4 - Input Taxed Sales
        Input taxed sales (financial services, residential rent)
        """
        input_taxed_codes = self._get_tax_codes_for_type(TaxType.INPUT_TAXED)
        tax_code_ids = [tc.id for tc in input_taxed_codes]
        
        # Get input taxed sales from invoices
        invoice_input_taxed = db.session.query(func.sum(Invoice.total)).filter(
            Invoice.organization_id == self.organization_id,
            Invoice.invoice_date.between(self.start_date, self.end_date),
            Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PAID]),
            Invoice.line_items.any(InvoiceLineItem.tax_code_id.in_(tax_code_ids))
        ).scalar() or Decimal('0')
        
        # Get input taxed sales from journal entries
        journal_input_taxed = db.session.query(func.sum(JournalLineItem.credit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type == AccountType.REVENUE,
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(invoice_input_taxed + journal_input_taxed, 2)
    
    def calculate_g10(self):
        """
        G10 - Capital Purchases (GST Inclusive)
        Capital purchases including GST
        """
        gst_tax_codes = self._get_tax_codes_for_type(TaxType.GST_STANDARD)
        capital_tax_codes = self._get_tax_codes_for_type(TaxType.CAPITAL_ACQUISITION)
        tax_code_ids = [tc.id for tc in gst_tax_codes + capital_tax_codes]
        
        # Get capital purchases from journal entries
        capital_purchases = db.session.query(func.sum(JournalLineItem.debit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type.in_([AccountType.ASSET, AccountType.FIXED_ASSET]),
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(capital_purchases, 2)
    
    def calculate_g11(self):
        """
        G11 - Non-Capital Purchases (GST Inclusive)
        Operating expenses and inventory purchases with GST
        """
        gst_tax_codes = self._get_tax_codes_for_type(TaxType.GST_STANDARD)
        tax_code_ids = [tc.id for tc in gst_tax_codes]
        
        # Get non-capital purchases from journal entries
        non_capital_purchases = db.session.query(func.sum(JournalLineItem.debit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type.in_([AccountType.EXPENSE, AccountType.COST_OF_GOODS_SOLD]),
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(non_capital_purchases, 2)
    
    def calculate_g13(self):
        """
        G13 - Credit Purchases for Input Taxed Sales
        Purchases related to making input taxed sales
        """
        # This requires specific allocation logic based on business rules
        # For now, return 0 unless specifically configured
        return Decimal('0')
    
    def calculate_g14(self):
        """
        G14 - Purchases Without GST
        GST-free purchases and imports
        """
        gst_free_tax_codes = self._get_tax_codes_for_type(TaxType.GST_FREE)
        export_tax_codes = self._get_tax_codes_for_type(TaxType.EXPORT)
        tax_code_ids = [tc.id for tc in gst_free_tax_codes + export_tax_codes]
        
        # Get GST-free purchases from journal entries
        gst_free_purchases = db.session.query(func.sum(JournalLineItem.debit)).join(
            JournalEntry
        ).join(Account).filter(
            JournalEntry.organization_id == self.organization_id,
            JournalEntry.date.between(self.start_date, self.end_date),
            Account.type.in_([AccountType.EXPENSE, AccountType.COST_OF_GOODS_SOLD, AccountType.ASSET]),
            JournalLineItem.tax_code_id.in_(tax_code_ids)
        ).scalar() or Decimal('0')
        
        return round(gst_free_purchases, 2)
    
    def calculate_1a(self):
        """
        1A - GST on Sales
        GST collected on sales (extract from GST-inclusive amounts)
        """
        g1_total = self.calculate_g1()
        # For GST-inclusive amounts: GST = amount ÷ 11
        gst_on_sales = g1_total / self.GST_DIVISOR
        return round(gst_on_sales, 2)
    
    def calculate_1b(self):
        """
        1B - GST on Purchases (Input Tax Credits)
        GST paid on purchases that can be claimed as credits
        """
        g10_total = self.calculate_g10()
        g11_total = self.calculate_g11()
        total_gst_purchases = g10_total + g11_total
        
        # For GST-inclusive amounts: GST = amount ÷ 11
        gst_on_purchases = total_gst_purchases / self.GST_DIVISOR
        return round(gst_on_purchases, 2)
    
    def calculate_adjustments(self):
        """
        Calculate any BAS adjustments
        This would include corrections from previous periods
        """
        # For now, return 0 unless specific adjustments are recorded
        return Decimal('0')
    
    def calculate_net_gst(self):
        """
        Net GST position (amount owed to or refund from ATO)
        Positive = Amount owed to ATO
        Negative = Refund from ATO
        """
        gst_on_sales = self.calculate_1a()
        gst_on_purchases = self.calculate_1b()
        adjustments = self.calculate_adjustments()
        
        net_gst = gst_on_sales - gst_on_purchases + adjustments
        return round(net_gst, 2)
    
    def validate_bas_data(self):
        """
        Validate BAS calculations for accuracy
        """
        validations = []
        
        # Check G1 vs 1A relationship
        g1 = self.calculate_g1()
        one_a = self.calculate_1a()
        expected_1a = g1 / self.GST_DIVISOR
        
        if abs(one_a - expected_1a) > Decimal('0.01'):
            validations.append(f"1A calculation ({one_a}) doesn't match G1 ÷ 11 ({expected_1a})")
        
        # Check purchase GST calculation
        g10 = self.calculate_g10()
        g11 = self.calculate_g11()
        one_b = self.calculate_1b()
        expected_1b = (g10 + g11) / self.GST_DIVISOR
        
        if abs(one_b - expected_1b) > Decimal('0.01'):
            validations.append(f"1B calculation ({one_b}) doesn't match (G10 + G11) ÷ 11 ({expected_1b})")
        
        # Check for negative amounts (which shouldn't occur)
        fields_to_check = {
            'G1': g1, 'G10': g10, 'G11': g11,
            '1A': one_a, '1B': one_b
        }
        
        for field_name, value in fields_to_check.items():
            if value < 0:
                validations.append(f"{field_name} has negative value: {value}")
        
        # Check quarter alignment
        if self.end_date.month not in [3, 6, 9, 12]:
            validations.append("BAS period should end on a quarter end (March, June, September, December)")
        
        return validations
    
    def generate_bas_report(self):
        """
        Generate complete BAS report with all calculations
        """
        # Calculate all fields
        g1 = self.calculate_g1()
        g2 = self.calculate_g2()
        g3 = self.calculate_g3()
        g4 = self.calculate_g4()
        g7 = self.calculate_adjustments()
        
        g10 = self.calculate_g10()
        g11 = self.calculate_g11()
        g13 = self.calculate_g13()
        g14 = self.calculate_g14()
        
        one_a = self.calculate_1a()
        one_b = self.calculate_1b()
        net_gst = self.calculate_net_gst()
        
        validations = self.validate_bas_data()
        
        return {
            'period': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'quarter': self.quarter
            },
            'sales': {
                'G1': float(g1),
                'G2': float(g2),
                'G3': float(g3),
                'G4': float(g4),
                'G7': float(g7),
                'total_sales': float(g1 + g2 + g3 + g4)
            },
            'purchases': {
                'G10': float(g10),
                'G11': float(g11),
                'G13': float(g13),
                'G14': float(g14),
                'total_purchases': float(g10 + g11 + g13 + g14)
            },
            'gst': {
                '1A': float(one_a),
                '1B': float(one_b),
                'net_gst': float(net_gst),
                'gst_rate': float(self.GST_RATE),
                'status': 'refund' if net_gst < 0 else 'payable' if net_gst > 0 else 'nil'
            },
            'validation': {
                'errors': validations,
                'is_valid': len(validations) == 0
            },
            'summary': {
                'gst_inclusive_sales': float(g1),
                'gst_free_sales': float(g2 + g3 + g4),
                'gst_inclusive_purchases': float(g10 + g11),
                'gst_liability': float(net_gst),
                'quarter_display': self.quarter
            }
        }
    
@reports_bp.route('/australian-gst-bas')
@login_required
def australian_gst_bas():
    """Australian GST Business Activity Statement (BAS) Report"""
    period = request.args.get('period', 'this_quarter')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Get date range
    start_date, end_date = get_date_range(period, start_date, end_date)
    
    # Generate BAS report
    bas_generator = AustralianGSTBASReport(
        start_date=start_date,
        end_date=end_date,
        organization_id=current_user.organization_id
    )
    
    bas_data = bas_generator.generate_bas_report()
    
    # Get available tax codes for reference
    tax_codes = TaxCode.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    ).order_by(TaxCode.tax_type, TaxCode.code).all()
    
    return render_template('reports/australian_gst_bas.html', 
                         bas_data=bas_data,
                         tax_codes=tax_codes,
                         period=period,
                         start_date=start_date,
                         end_date=end_date)

@reports_bp.route('/australian-gst-bas/export')
@login_required
def export_australian_gst_bas():
    """Export Australian GST BAS Report to CSV"""
    period = request.args.get('period', 'this_quarter')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Get date range
    start_date, end_date = get_date_range(period, start_date, end_date)
    
    # Generate BAS report
    bas_generator = AustralianGSTBASReport(
        start_date=start_date,
        end_date=end_date,
        organization_id=current_user.organization_id
    )
    
    bas_data = bas_generator.generate_bas_report()
    
    # Create CSV response
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Australian GST Business Activity Statement (BAS)'])
    writer.writerow([f"Period: {bas_data['period']['start_date']} to {bas_data['period']['end_date']}"])
    writer.writerow([f"Quarter: {bas_data['period']['quarter']}"])
    writer.writerow([])
    
    # Sales section
    writer.writerow(['SALES AND INCOME'])
    writer.writerow(['Field', 'Description', 'Amount (AUD)'])
    writer.writerow(['G1', 'Total sales (including GST)', f"${bas_data['sales']['G1']:,.2f}"])
    writer.writerow(['G2', 'Export sales', f"${bas_data['sales']['G2']:,.2f}"])
    writer.writerow(['G3', 'Other GST-free sales', f"${bas_data['sales']['G3']:,.2f}"])
    writer.writerow(['G4', 'Input taxed sales', f"${bas_data['sales']['G4']:,.2f}"])
    writer.writerow(['G7', 'Adjustments', f"${bas_data['sales']['G7']:,.2f}"])
    writer.writerow([])
    
    # Purchases section
    writer.writerow(['PURCHASES AND EXPENSES'])
    writer.writerow(['Field', 'Description', 'Amount (AUD)'])
    writer.writerow(['G10', 'Capital purchases (including GST)', f"${bas_data['purchases']['G10']:,.2f}"])
    writer.writerow(['G11', 'Non-capital purchases (including GST)', f"${bas_data['purchases']['G11']:,.2f}"])
    writer.writerow(['G13', 'Purchases for input taxed sales', f"${bas_data['purchases']['G13']:,.2f}"])
    writer.writerow(['G14', 'Purchases without GST', f"${bas_data['purchases']['G14']:,.2f}"])
    writer.writerow([])
    
    # GST calculations
    writer.writerow(['GST CALCULATIONS'])
    writer.writerow(['Field', 'Description', 'Amount (AUD)'])
    writer.writerow(['1A', 'GST on sales', f"${bas_data['gst']['1A']:,.2f}"])
    writer.writerow(['1B', 'GST on purchases', f"${bas_data['gst']['1B']:,.2f}"])
    writer.writerow(['', 'Net GST amount', f"${bas_data['gst']['net_gst']:,.2f}"])
    writer.writerow(['', 'Status', bas_data['gst']['status'].title()])
    writer.writerow([])
    
    # Validation
    if bas_data['validation']['errors']:
        writer.writerow(['VALIDATION ERRORS'])
        for error in bas_data['validation']['errors']:
            writer.writerow(['', error])
    else:
        writer.writerow(['VALIDATION: PASSED'])
    
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=australian_gst_bas_{bas_data["period"]["quarter"]}.csv'
    
    return response

@reports_bp.route('/tax-codes')
@login_required
def tax_codes_report():
    """Tax Codes Configuration Report"""
    tax_codes = TaxCode.query.filter_by(
        organization_id=current_user.organization_id
    ).order_by(TaxCode.tax_type, TaxCode.code).all()
    
    # Group by tax type
    tax_codes_by_type = {}
    for tax_code in tax_codes:
        tax_type = tax_code.tax_type.value
        if tax_type not in tax_codes_by_type:
            tax_codes_by_type[tax_type] = []
        tax_codes_by_type[tax_type].append(tax_code)
    
    return render_template('reports/tax_codes.html', 
                         tax_codes_by_type=tax_codes_by_type,
                         tax_types=TaxType)

@reports_bp.route('/api/seed-australian-tax-codes', methods=['POST'])
@login_required
def seed_australian_tax_codes():
    """Seed standard Australian GST tax codes"""
    try:
        # Check if tax codes already exist
        existing_codes = TaxCode.query.filter_by(
            organization_id=current_user.organization_id
        ).count()
        
        if existing_codes > 0:
            return jsonify({
                'success': False,
                'message': 'Tax codes already exist for this organization'
            })
        
        # Standard Australian GST tax codes
        standard_tax_codes = [
            {
                'code': 'GST',
                'name': 'GST Standard Rate',
                'description': 'Standard 10% GST rate for most goods and services',
                'tax_type': TaxType.GST_STANDARD,
                'rate': Decimal('0.10'),
                'is_inclusive': True
            },
            {
                'code': 'FRE',
                'name': 'GST-Free',
                'description': 'GST-free supplies (food, medical, education)',
                'tax_type': TaxType.GST_FREE,
                'rate': Decimal('0.00'),
                'is_inclusive': False
            },
            {
                'code': 'EXP',
                'name': 'Export Sales',
                'description': 'GST-free export sales',
                'tax_type': TaxType.EXPORT,
                'rate': Decimal('0.00'),
                'is_inclusive': False
            },
            {
                'code': 'INP',
                'name': 'Input Taxed',
                'description': 'Input taxed supplies (financial services, residential rent)',
                'tax_type': TaxType.INPUT_TAXED,
                'rate': Decimal('0.00'),
                'is_inclusive': False
            },
            {
                'code': 'CAP',
                'name': 'Capital Acquisition',
                'description': 'Capital purchases and acquisitions with GST',
                'tax_type': TaxType.CAPITAL_ACQUISITION,
                'rate': Decimal('0.10'),
                'is_inclusive': True
            }
        ]
        
        # Create tax codes
        for tax_code_data in standard_tax_codes:
            tax_code = TaxCode(
                organization_id=current_user.organization_id,
                **tax_code_data
            )
            db.session.add(tax_code)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully created {len(standard_tax_codes)} Australian GST tax codes'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error seeding tax codes: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error creating tax codes: {str(e)}'
        }), 500
