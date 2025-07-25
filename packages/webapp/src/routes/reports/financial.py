
from flask import Blueprint, render_template
financial_bp = Blueprint('financial', __name__)

# Trial Balance route (for reports.financial.trial_balance endpoint)
@financial_bp.route('/trial-balance')
def trial_balance():
    # TODO: Replace with real data and template
    return render_template('reports/financial/trial_balance.html')


# General Ledger route (for reports.financial.general_ledger endpoint)
@financial_bp.route('/general-ledger')
def general_ledger():
    # TODO: Replace with real data and template
    # Provide safe fallbacks for required context variables
    from datetime import date
    report_period = {
        'start_date': date.today(),
        'end_date': date.today()
    }
    report_data = {
        'account': None,
        'accounts': [],
        'ledger_entries': [],
        'opening_balance': 0.0,
        'closing_balance': 0.0,
        'total_debits': 0.0,
        'total_credits': 0.0,
        'net_change': 0.0
    }
    return render_template('reports/tax-compliance/general_ledger.html', report_period=report_period, report_data=report_data)

# Cash Flow Statement route (for reports.financial.cash_flow endpoint)
from datetime import date
@financial_bp.route('/cash-flow')
@financial_bp.route('/cash-flow/<format>')
def cash_flow(format=None):
    # TODO: Replace with real data and template
    today = date.today()
    report_period = {
        'start_date': today,
        'end_date': today
    }
    # Placeholder for export logic
    if format == 'pdf':
        # TODO: Implement PDF export
        pass
    elif format == 'excel':
        # TODO: Implement Excel export
        pass
    elif format == 'csv':
        # TODO: Implement CSV export
        pass
    report_data = generate_cash_flow_data(report_period['start_date'], report_period['end_date'])
    return render_template('reports/financial/cash_flow.html', report_period=report_period, report_data=report_data)
# --- Cash Flow Data Generation ---
def generate_cash_flow_data(start_date, end_date):
    """Generate cash flow statement data from database, fallback to zeros if no data."""
    # Structure: operating, investing, financing, net_cash_flow
    try:
        from packages.server.src.models import Account, AccountType, JournalEntry, JournalLineItem, db
        from sqlalchemy import func
        # Get all cash/bank accounts
        cash_accounts = Account.query.filter(Account.type.in_([AccountType.BANK, AccountType.CASH])).all()
        cash_account_ids = [a.id for a in cash_accounts]
        # Query all cash-related journal line items in date range
        q = db.session.query(
            JournalLineItem.account_id,
            func.sum(JournalLineItem.amount).label('amount')
        ).join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
        q = q.filter(JournalLineItem.account_id.in_(cash_account_ids))
        q = q.filter(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
        q = q.group_by(JournalLineItem.account_id)
        cash_movements = q.all()
        # For now, treat all as operating activities
        operating_activities = [
            {
                'account_id': row.account_id,
                'amount': float(row.amount) if row.amount else 0.0
            } for row in cash_movements
        ]
        total_operating = sum(item['amount'] for item in operating_activities)
        # No data for investing/financing in this placeholder
        total_investing = 0.0
        total_financing = 0.0
        net_cash_flow = total_operating
        # Fallbacks if no data
        if not operating_activities:
            operating_activities = [{'account_id': None, 'amount': 0.0}]
        return {
            'operating_activities': operating_activities,
            'investing_activities': [],
            'financing_activities': [],
            'net_cash_flow': net_cash_flow,
            'total_operating': total_operating,
            'total_investing': total_investing,
            'total_financing': total_financing
        }
    except Exception as e:
        print(f"Error generating cash flow data: {e}")
        return {
            'operating_activities': [{'account_id': None, 'amount': 0.0}],
            'investing_activities': [],
            'financing_activities': [],
            'net_cash_flow': 0.0,
            'total_operating': 0.0,
            'total_investing': 0.0,
            'total_financing': 0.0
        }

# Balance Sheet route (for reports.financial.balance_sheet endpoint)
from datetime import date
@financial_bp.route('/balance-sheet')
def balance_sheet():
    # Use today's date as the report period end date
    report_period = {
        'end_date': date.today()
    }
    # Query the database for assets, liabilities, and equity accounts and balances
    try:
        assets = get_accounts_with_balances(AccountType.ASSET, None, None)
        liabilities = get_accounts_with_balances(AccountType.LIABILITY, None, None)
        equity = get_accounts_with_balances(AccountType.EQUITY, None, None)
        total_assets = sum(a['balance'] for a in assets) if assets else 0.0
        total_liabilities = sum(l['balance'] for l in liabilities) if liabilities else 0.0
        total_equity = sum(e['balance'] for e in equity) if equity else 0.0
        report_data = {
            'assets': [
                {
                    'id': a.id,
                    'name': a.name,
                    'code': getattr(a, 'code', ''),
                    'balance': float(a.balance) if a.balance else 0.0
                } for a in assets
            ],
            'liabilities': [
                {
                    'id': l.id,
                    'name': l.name,
                    'code': getattr(l, 'code', ''),
                    'balance': float(l.balance) if l.balance else 0.0
                } for l in liabilities
            ],
            'equity': [
                {
                    'id': e.id,
                    'name': e.name,
                    'code': getattr(e, 'code', ''),
                    'balance': float(e.balance) if e.balance else 0.0
                } for e in equity
            ],
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'retained_earnings': 0.0,
            'total_liabilities_equity': total_liabilities + total_equity
        }
    except Exception as ex:
        print(f"Error generating balance sheet data: {ex}")
        report_data = {
            'assets': [],
            'liabilities': [],
            'equity': [],
            'total_assets': 0.0,
            'total_liabilities': 0.0,
            'total_equity': 0.0,
            'retained_earnings': 0.0,
            'total_liabilities_equity': 0.0
        }
    return render_template('reports/financial/balance_sheet.html', report_period=report_period, report_data=report_data)


# Profit & Loss Statement route (for reports.financial.profit_loss endpoint)

from flask import request
from datetime import datetime, timedelta
from packages.server.src.models import db, Account, AccountType, JournalEntry, JournalLineItem
from sqlalchemy import func

@financial_bp.route('/profit-loss')
@financial_bp.route('/profit-loss/<format>')
def profit_loss(format=None):
    # Get dates from request parameters or use defaults
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
    else:
        # Default to last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    # Generate the report data with actual database queries
    report_data = generate_profit_loss_data(start_date, end_date)
    if format == 'pdf':
        # Placeholder for PDF export logic
        return generate_pdf_report(report_data)
    return render_template('reports/financial/profit_loss.html', 
                         report_period=report_period,
                         report_data=report_data)

def generate_profit_loss_data(start_date, end_date):
    """Generate profit & loss report data from database with fallback to zeros"""
    report_data = {
        'income_accounts': [],
        'expense_accounts': [],
        'cogs_accounts': [],
        'expense_categories': [],
        'other_income_accounts': [],
        'other_expense_accounts': [],
        'total_income': 0.0,
        'total_expenses': 0.0,
        'total_cogs': 0.0,
        'gross_profit': 0.0,
        'total_other_income': 0.0,
        'total_other_expenses': 0.0,
        'net_profit': 0.0,
        'gross_profit_margin': 0.0,
        'net_profit_margin': 0.0
    }
    try:
        income_results = get_accounts_with_balances(AccountType.INCOME, start_date, end_date)
        expense_results = get_accounts_with_balances(AccountType.EXPENSE, start_date, end_date)
        report_data['income_accounts'] = [
            {
                'id': result.id,
                'name': result.name,
                'code': getattr(result, 'code', ''),
                'balance': float(result.balance) if result.balance else 0.0
            }
            for result in income_results
        ]
        report_data['expense_accounts'] = [
            {
                'id': result.id,
                'name': result.name,
                'code': getattr(result, 'code', ''),
                'balance': float(result.balance) if result.balance else 0.0
            }
            for result in expense_results
        ]
        report_data['total_income'] = sum(account['balance'] for account in report_data['income_accounts'])
        report_data['total_expenses'] = sum(account['balance'] for account in report_data['expense_accounts'])
        # TODO: Implement actual COGS, categories, and other income/expense logic
        report_data['total_cogs'] = 0.0
        report_data['gross_profit'] = report_data['total_income'] - report_data['total_cogs']
        report_data['total_other_income'] = 0.0
        report_data['total_other_expenses'] = 0.0
        report_data['net_profit'] = report_data['gross_profit'] - report_data['total_expenses']
        # Margins (avoid division by zero)
        report_data['gross_profit_margin'] = (
            (report_data['gross_profit'] / report_data['total_income'] * 100)
            if report_data['total_income'] else 0.0
        )
        report_data['net_profit_margin'] = (
            (report_data['net_profit'] / report_data['total_income'] * 100)
            if report_data['total_income'] else 0.0
        )
        if not report_data['income_accounts']:
            report_data['income_accounts'] = [
                {'name': 'No income accounts found for this period', 'code': '', 'balance': 0.0}
            ]
        if not report_data['expense_accounts']:
            report_data['expense_accounts'] = [
                {'name': 'No expense accounts found for this period', 'code': '', 'balance': 0.0}
            ]
    except Exception as e:
        print(f"Error generating profit loss data: {e}")
        report_data['income_accounts'] = [
            {'name': 'Error loading income accounts', 'code': '', 'balance': 0.0}
        ]
        report_data['expense_accounts'] = [
            {'name': 'Error loading expense accounts', 'code': '', 'balance': 0.0}
        ]
    return report_data

def get_accounts_with_balances(account_type, start_date, end_date):
    """
    Get accounts of specified type with their balances for the given date range.
    Returns accounts even if they have zero balances.
    """
    try:
        all_accounts = Account.query.filter_by(type=account_type).all()
        if not all_accounts:
            return []
        accounts_with_balances = (
            db.session.query(
                Account.id,
                Account.name,
                Account.code,
                func.coalesce(func.sum(JournalLineItem.amount), 0).label('balance')
            )
            .outerjoin(JournalLineItem, JournalLineItem.account_id == Account.id)
            .outerjoin(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
            .filter(Account.type == account_type)
            .filter(
                db.or_(
                    JournalEntry.date.is_(None),
                    db.and_(
                        JournalEntry.date >= start_date,
                        JournalEntry.date <= end_date
                    )
                )
            )
            .group_by(Account.id, Account.name, Account.code)
            .all()
        )
        return accounts_with_balances
    except Exception as e:
        print(f"Error querying accounts with balances: {e}")
        return []

# Placeholder for PDF export
def generate_pdf_report(report_data):
    return "PDF export not implemented yet"

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
