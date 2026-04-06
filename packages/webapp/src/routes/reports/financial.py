"""
Financial reports routes - Trial Balance, General Ledger, Cash Flow, Balance Sheet, P&L
"""

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, or_

from packages.server.src.models import (
    db, Account, AccountType, JournalEntry, JournalLineItem
)

financial_bp = Blueprint('financial', __name__)


# --- Trial Balance ---

@financial_bp.route('/trial-balance')
@login_required
def trial_balance():
    as_of_date_str = request.args.get('as_of_date')
    if as_of_date_str:
        try:
            as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
        except ValueError:
            as_of_date = date.today()
    else:
        as_of_date = date.today()

    # Query all accounts with their debit and credit totals from journal line items
    results = (
        db.session.query(
            Account.id,
            Account.code,
            Account.name,
            Account.type,
            func.coalesce(func.sum(JournalLineItem.debit), 0).label('total_debits'),
            func.coalesce(func.sum(JournalLineItem.credit), 0).label('total_credits')
        )
        .outerjoin(JournalLineItem, JournalLineItem.account_id == Account.id)
        .outerjoin(JournalEntry, and_(
            JournalLineItem.journal_entry_id == JournalEntry.id,
            JournalEntry.date <= as_of_date
        ))
        .filter(Account.organization_id == current_user.organization_id)
        .group_by(Account.id, Account.code, Account.name, Account.type)
        .order_by(Account.code)
        .all()
    )

    trial_balance_data = []
    total_debits = Decimal('0.00')
    total_credits = Decimal('0.00')

    for row in results:
        debits = Decimal(str(row.total_debits))
        credits = Decimal(str(row.total_credits))
        net = debits - credits

        # Determine debit/credit balance based on account type
        # Assets and Expenses normally have debit balances
        # Liabilities, Equity, and Income normally have credit balances
        if net == 0:
            continue  # Skip zero-balance accounts

        if net > 0:
            debit_balance = net
            credit_balance = Decimal('0.00')
        else:
            debit_balance = Decimal('0.00')
            credit_balance = abs(net)

        trial_balance_data.append({
            'account_id': row.id,
            'account_code': row.code,
            'account_name': row.name,
            'account_type': row.type.value if row.type else '',
            'debit_balance': float(debit_balance),
            'credit_balance': float(credit_balance)
        })

        total_debits += debit_balance
        total_credits += credit_balance

    is_balanced = abs(total_debits - total_credits) < Decimal('0.01')

    report_data = {
        'as_of_date': as_of_date.isoformat(),
        'trial_balance_data': trial_balance_data,
        'total_debits': float(total_debits),
        'total_credits': float(total_credits),
        'is_balanced': is_balanced
    }

    return render_template('reports/tax-compliance/trial_balance.html', report_data=report_data)


# --- General Ledger ---

@financial_bp.route('/general-ledger')
@login_required
def general_ledger():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    account_id = request.args.get('account_id')

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # Get all accounts for filter dropdown
    accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.is_active == True
    ).order_by(Account.code).all()

    # Get selected account
    selected_account = None
    if account_id:
        selected_account = Account.query.filter(
            Account.id == account_id,
            Account.organization_id == current_user.organization_id
        ).first()

    # Build ledger entries
    ledger_entries = []
    opening_balance = Decimal('0.00')
    total_debits = Decimal('0.00')
    total_credits = Decimal('0.00')

    if selected_account:
        # Calculate opening balance (all entries before start_date)
        opening_result = (
            db.session.query(
                func.coalesce(func.sum(JournalLineItem.debit), 0).label('debits'),
                func.coalesce(func.sum(JournalLineItem.credit), 0).label('credits')
            )
            .join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
            .filter(
                JournalLineItem.account_id == selected_account.id,
                JournalEntry.date < start_date,
                JournalEntry.organization_id == current_user.organization_id
            )
            .first()
        )
        if opening_result:
            opening_balance = Decimal(str(opening_result.debits)) - Decimal(str(opening_result.credits))

        # Get journal line items for the date range
        entries = (
            db.session.query(
                JournalEntry.date,
                JournalEntry.entry_number,
                JournalEntry.description.label('entry_description'),
                JournalEntry.source_type,
                JournalLineItem.description.label('line_description'),
                JournalLineItem.debit,
                JournalLineItem.credit,
                JournalLineItem.contact_type,
                JournalLineItem.contact_id
            )
            .join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
            .filter(
                JournalLineItem.account_id == selected_account.id,
                JournalEntry.date >= start_date,
                JournalEntry.date <= end_date,
                JournalEntry.organization_id == current_user.organization_id
            )
            .order_by(JournalEntry.date, JournalEntry.id)
            .all()
        )

        running_balance = opening_balance
        for entry in entries:
            debit = Decimal(str(entry.debit or 0))
            credit = Decimal(str(entry.credit or 0))
            running_balance += debit - credit
            total_debits += debit
            total_credits += credit

            ledger_entries.append({
                'date': entry.date,
                'entry_number': entry.entry_number,
                'description': entry.line_description or entry.entry_description,
                'source_type': entry.source_type or '',
                'debit': float(debit),
                'credit': float(credit),
                'balance': float(running_balance)
            })

    closing_balance = opening_balance + total_debits - total_credits

    report_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    report_data = {
        'account': selected_account,
        'accounts': accounts,
        'ledger_entries': ledger_entries,
        'opening_balance': float(opening_balance),
        'closing_balance': float(closing_balance),
        'total_debits': float(total_debits),
        'total_credits': float(total_credits),
        'net_change': float(total_debits - total_credits)
    }

    return render_template('reports/tax-compliance/general_ledger.html',
                         report_period=report_period, report_data=report_data)


# --- Cash Flow Statement ---

@financial_bp.route('/cash-flow')
@financial_bp.route('/cash-flow/<format>')
@login_required
def cash_flow(format=None):
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    report_period = {'start_date': start_date, 'end_date': end_date}
    report_data = generate_cash_flow_data(start_date, end_date)

    return render_template('reports/financial/cash_flow.html',
                         report_period=report_period, report_data=report_data)


def generate_cash_flow_data(start_date, end_date):
    """Generate cash flow statement from journal entries, categorized by activity."""
    try:
        org_id = current_user.organization_id

        # Operating activities: Income and Expense account movements
        operating = (
            db.session.query(
                Account.name,
                func.coalesce(func.sum(JournalLineItem.debit), 0).label('debits'),
                func.coalesce(func.sum(JournalLineItem.credit), 0).label('credits')
            )
            .join(JournalLineItem, JournalLineItem.account_id == Account.id)
            .join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
            .filter(
                Account.organization_id == org_id,
                Account.type.in_([AccountType.INCOME, AccountType.EXPENSE]),
                JournalEntry.date >= start_date,
                JournalEntry.date <= end_date
            )
            .group_by(Account.id, Account.name)
            .all()
        )

        operating_activities = []
        total_operating = Decimal('0.00')
        for row in operating:
            # For income: credits are positive cash flow
            # For expenses: debits are negative cash flow
            net = Decimal(str(row.credits)) - Decimal(str(row.debits))
            if net != 0:
                operating_activities.append({
                    'name': row.name,
                    'amount': float(net)
                })
                total_operating += net

        # AR/AP changes (operating)
        ar_ap_change = (
            db.session.query(
                Account.name,
                Account.type,
                func.coalesce(func.sum(JournalLineItem.debit), 0).label('debits'),
                func.coalesce(func.sum(JournalLineItem.credit), 0).label('credits')
            )
            .join(JournalLineItem, JournalLineItem.account_id == Account.id)
            .join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
            .filter(
                Account.organization_id == org_id,
                Account.type.in_([AccountType.ASSET, AccountType.LIABILITY]),
                or_(
                    Account.name.ilike('%receivable%'),
                    Account.name.ilike('%payable%')
                ),
                JournalEntry.date >= start_date,
                JournalEntry.date <= end_date
            )
            .group_by(Account.id, Account.name, Account.type)
            .all()
        )

        for row in ar_ap_change:
            debits = Decimal(str(row.debits))
            credits = Decimal(str(row.credits))
            if row.type == AccountType.ASSET:
                # Increase in AR = negative cash flow
                net = credits - debits
            else:
                # Increase in AP = positive cash flow
                net = credits - debits
            if net != 0:
                operating_activities.append({
                    'name': f'Change in {row.name}',
                    'amount': float(net)
                })
                total_operating += net

        # Investing activities: Fixed asset changes
        investing = (
            db.session.query(
                Account.name,
                func.coalesce(func.sum(JournalLineItem.debit), 0).label('debits'),
                func.coalesce(func.sum(JournalLineItem.credit), 0).label('credits')
            )
            .join(JournalLineItem, JournalLineItem.account_id == Account.id)
            .join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
            .filter(
                Account.organization_id == org_id,
                Account.type == AccountType.ASSET,
                ~Account.name.ilike('%receivable%'),
                ~Account.name.ilike('%cash%'),
                ~Account.name.ilike('%bank%'),
                ~Account.name.ilike('%checking%'),
                ~Account.name.ilike('%savings%'),
                JournalEntry.date >= start_date,
                JournalEntry.date <= end_date
            )
            .group_by(Account.id, Account.name)
            .all()
        )

        investing_activities = []
        total_investing = Decimal('0.00')
        for row in investing:
            net = Decimal(str(row.credits)) - Decimal(str(row.debits))
            if net != 0:
                investing_activities.append({
                    'name': row.name,
                    'amount': float(net)
                })
                total_investing += net

        # Financing activities: Equity and non-AP liability changes
        financing = (
            db.session.query(
                Account.name,
                func.coalesce(func.sum(JournalLineItem.debit), 0).label('debits'),
                func.coalesce(func.sum(JournalLineItem.credit), 0).label('credits')
            )
            .join(JournalLineItem, JournalLineItem.account_id == Account.id)
            .join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
            .filter(
                Account.organization_id == org_id,
                or_(
                    Account.type == AccountType.EQUITY,
                    and_(
                        Account.type == AccountType.LIABILITY,
                        ~Account.name.ilike('%payable%')
                    )
                ),
                JournalEntry.date >= start_date,
                JournalEntry.date <= end_date
            )
            .group_by(Account.id, Account.name)
            .all()
        )

        financing_activities = []
        total_financing = Decimal('0.00')
        for row in financing:
            net = Decimal(str(row.credits)) - Decimal(str(row.debits))
            if net != 0:
                financing_activities.append({
                    'name': row.name,
                    'amount': float(net)
                })
                total_financing += net

        net_cash_flow = total_operating + total_investing + total_financing

        return {
            'operating_activities': operating_activities,
            'investing_activities': investing_activities,
            'financing_activities': financing_activities,
            'total_operating': float(total_operating),
            'total_investing': float(total_investing),
            'total_financing': float(total_financing),
            'net_cash_flow': float(net_cash_flow)
        }

    except Exception as e:
        print(f"Error generating cash flow data: {e}")
        return {
            'operating_activities': [],
            'investing_activities': [],
            'financing_activities': [],
            'total_operating': 0.0,
            'total_investing': 0.0,
            'total_financing': 0.0,
            'net_cash_flow': 0.0
        }


# --- Balance Sheet ---

@financial_bp.route('/balance-sheet')
@login_required
def balance_sheet():
    as_of_date_str = request.args.get('as_of_date')
    if as_of_date_str:
        try:
            as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
        except ValueError:
            as_of_date = date.today()
    else:
        as_of_date = date.today()

    report_period = {'end_date': as_of_date}

    try:
        assets = get_accounts_with_balances(AccountType.ASSET, None, as_of_date)
        liabilities = get_accounts_with_balances(AccountType.LIABILITY, None, as_of_date)
        equity = get_accounts_with_balances(AccountType.EQUITY, None, as_of_date)

        # Calculate retained earnings (net income not yet in equity)
        income_total = sum_account_balances(AccountType.INCOME, None, as_of_date)
        expense_total = sum_account_balances(AccountType.EXPENSE, None, as_of_date)
        retained_earnings = income_total - expense_total

        total_assets = sum(float(a.balance) for a in assets) if assets else 0.0
        total_liabilities = sum(float(l.balance) for l in liabilities) if liabilities else 0.0
        total_equity = sum(float(e.balance) for e in equity) if equity else 0.0

        report_data = {
            'assets': [{'id': a.id, 'name': a.name, 'code': a.code or '', 'balance': float(a.balance)} for a in assets],
            'liabilities': [{'id': l.id, 'name': l.name, 'code': l.code or '', 'balance': float(l.balance)} for l in liabilities],
            'equity': [{'id': e.id, 'name': e.name, 'code': e.code or '', 'balance': float(e.balance)} for e in equity],
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'retained_earnings': float(retained_earnings),
            'total_liabilities_equity': total_liabilities + total_equity + float(retained_earnings)
        }
    except Exception as ex:
        print(f"Error generating balance sheet data: {ex}")
        report_data = {
            'assets': [], 'liabilities': [], 'equity': [],
            'total_assets': 0.0, 'total_liabilities': 0.0, 'total_equity': 0.0,
            'retained_earnings': 0.0, 'total_liabilities_equity': 0.0
        }

    return render_template('reports/financial/balance_sheet.html',
                         report_period=report_period, report_data=report_data)


# --- Profit & Loss ---

@financial_bp.route('/profit-loss')
@financial_bp.route('/profit-loss/<format>')
@login_required
def profit_loss(format=None):
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    report_period = {'start_date': start_date, 'end_date': end_date}
    report_data = generate_profit_loss_data(start_date, end_date)

    return render_template('reports/financial/profit_loss.html',
                         report_period=report_period, report_data=report_data)


def generate_profit_loss_data(start_date, end_date):
    """Generate P&L from actual journal entries."""
    report_data = {
        'income_accounts': [], 'expense_accounts': [],
        'cogs_accounts': [], 'expense_categories': [],
        'other_income_accounts': [], 'other_expense_accounts': [],
        'total_income': 0.0, 'total_expenses': 0.0,
        'total_cogs': 0.0, 'gross_profit': 0.0,
        'total_other_income': 0.0, 'total_other_expenses': 0.0,
        'net_profit': 0.0, 'gross_profit_margin': 0.0, 'net_profit_margin': 0.0
    }

    try:
        income_results = get_accounts_with_balances(AccountType.INCOME, start_date, end_date)
        expense_results = get_accounts_with_balances(AccountType.EXPENSE, start_date, end_date)

        report_data['income_accounts'] = [
            {'id': r.id, 'name': r.name, 'code': r.code or '', 'balance': float(r.balance)}
            for r in income_results
        ]
        report_data['expense_accounts'] = [
            {'id': r.id, 'name': r.name, 'code': r.code or '', 'balance': float(r.balance)}
            for r in expense_results
        ]

        report_data['total_income'] = sum(a['balance'] for a in report_data['income_accounts'])
        report_data['total_expenses'] = sum(a['balance'] for a in report_data['expense_accounts'])
        report_data['gross_profit'] = report_data['total_income'] - report_data['total_cogs']
        report_data['net_profit'] = report_data['gross_profit'] - report_data['total_expenses']

        if report_data['total_income'] > 0:
            report_data['gross_profit_margin'] = (report_data['gross_profit'] / report_data['total_income'] * 100)
            report_data['net_profit_margin'] = (report_data['net_profit'] / report_data['total_income'] * 100)

        if not report_data['income_accounts']:
            report_data['income_accounts'] = [{'name': 'No income for this period', 'code': '', 'balance': 0.0}]
        if not report_data['expense_accounts']:
            report_data['expense_accounts'] = [{'name': 'No expenses for this period', 'code': '', 'balance': 0.0}]

    except Exception as e:
        print(f"Error generating profit loss data: {e}")

    return report_data


# --- Helper Functions ---

def get_accounts_with_balances(account_type, start_date, end_date):
    """Get accounts with balances from journal entries."""
    try:
        org_id = current_user.organization_id
        query = (
            db.session.query(
                Account.id,
                Account.name,
                Account.code,
                func.coalesce(
                    func.sum(JournalLineItem.debit) - func.sum(JournalLineItem.credit), 0
                ).label('balance')
            )
            .outerjoin(JournalLineItem, JournalLineItem.account_id == Account.id)
            .outerjoin(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
            .filter(Account.type == account_type)
            .filter(Account.organization_id == org_id)
        )

        if start_date and end_date:
            query = query.filter(
                or_(
                    JournalEntry.date.is_(None),
                    and_(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
                )
            )
        elif end_date:
            query = query.filter(
                or_(
                    JournalEntry.date.is_(None),
                    JournalEntry.date <= end_date
                )
            )

        results = query.group_by(Account.id, Account.name, Account.code).all()

        # For liability/equity/income accounts, negate balance (they have credit-normal balances)
        if account_type in [AccountType.LIABILITY, AccountType.EQUITY, AccountType.INCOME]:
            # Return as namedtuple-like with negated balance
            class AccountBalance:
                def __init__(self, id, name, code, balance):
                    self.id = id
                    self.name = name
                    self.code = code
                    self.balance = balance
            return [AccountBalance(r.id, r.name, r.code, -float(r.balance) if r.balance else 0.0) for r in results if r.balance and float(r.balance) != 0]
        else:
            class AccountBalance:
                def __init__(self, id, name, code, balance):
                    self.id = id
                    self.name = name
                    self.code = code
                    self.balance = balance
            return [AccountBalance(r.id, r.name, r.code, float(r.balance) if r.balance else 0.0) for r in results if r.balance and float(r.balance) != 0]

    except Exception as e:
        print(f"Error querying accounts with balances: {e}")
        return []


def sum_account_balances(account_type, start_date, end_date):
    """Sum all balances for an account type."""
    accounts = get_accounts_with_balances(account_type, start_date, end_date)
    return sum(a.balance for a in accounts)


# Placeholder for PDF export
def generate_pdf_report(report_data):
    return "PDF export not implemented yet"
