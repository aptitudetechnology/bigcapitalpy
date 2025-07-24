"""
Financial Reports module for BigCapitalPy
Contains Profit & Loss, Balance Sheet, Cash Flow, Trial Balance, and General Ledger reports
"""

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func

from packages.server.src.models import (
    Account, AccountType, JournalEntry, JournalLineItem
)
from packages.server.src.database import db
from .utils import get_date_range, export_profit_loss_csv, calculate_account_balance

financial_bp = Blueprint('financial', __name__)


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
    from packages.server.src.models import Invoice, InvoiceStatus
    
    total = db.session.query(func.sum(Invoice.balance)).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE]),
        Invoice.balance > 0
    ).scalar() or Decimal('0.00')
    
    return total


@financial_bp.route('/profit-loss')
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
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net_profit': float(net_profit),
        'gross_profit': float(total_income),  # Simplified for now
        'cost_of_goods_sold': 0.0,
        'total_cogs': 0.0,
        'total_other_income': 0.0,
        'total_other_expenses': 0.0
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


@financial_bp.route('/balance-sheet')
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


@financial_bp.route('/cash-flow')
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


@financial_bp.route('/trial-balance')
@login_required
def trial_balance():
    """Trial Balance Report"""
    from datetime import datetime
    
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


@financial_bp.route('/general-ledger')
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