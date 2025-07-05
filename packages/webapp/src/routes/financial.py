"""
Financial routes for BigCapitalPy
Banking, Manual Journals, Reconciliation, and other financial operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, or_

from packages.server.src.models import (
    Account, AccountType, JournalEntry, JournalLineItem, 
    Customer, Vendor, Invoice, User
)
from packages.server.src.database import db

financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/')
@login_required
def index():
    """Financial dashboard with banking overview"""
    # Get cash accounts
    cash_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        or_(
            Account.name.ilike('%cash%'),
            Account.name.ilike('%bank%'),
            Account.name.ilike('%checking%'),
            Account.name.ilike('%savings%')
        ),
        Account.is_active == True
    ).all()
    
    # Calculate total cash balance
    total_cash = sum(account.current_balance or 0 for account in cash_accounts)
    
    # Get recent transactions (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    recent_transactions = JournalEntry.query.filter(
        JournalEntry.organization_id == current_user.organization_id,
        JournalEntry.date >= thirty_days_ago
    ).order_by(JournalEntry.date.desc()).limit(10).all()
    
    # Get unreconciled transactions count
    unreconciled_count = JournalEntry.query.filter(
        JournalEntry.organization_id == current_user.organization_id,
        JournalEntry.entry_number.like('BANK%')  # Bank transactions
    ).count()
    
    financial_data = {
        'cash_accounts': cash_accounts,
        'total_cash': total_cash,
        'recent_transactions': recent_transactions,
        'unreconciled_count': unreconciled_count,
        'accounts_count': len(cash_accounts)
    }
    
    return render_template('financial/index.html', data=financial_data)

@financial_bp.route('/banking')
@login_required
def banking():
    """Banking and bank accounts management"""
    # Get all bank accounts
    bank_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        or_(
            Account.name.ilike('%bank%'),
            Account.name.ilike('%checking%'),
            Account.name.ilike('%savings%'),
            Account.name.ilike('%cash%')
        ),
        Account.is_active == True
    ).order_by(Account.name).all()
    
    return render_template('financial/banking.html', accounts=bank_accounts)

@financial_bp.route('/manual-journals')
@login_required
def manual_journals():
    """Manual journal entries listing"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get manual journal entries
    journals = JournalEntry.query.filter(
        JournalEntry.organization_id == current_user.organization_id,
        JournalEntry.source_type == 'manual'
    ).order_by(JournalEntry.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('financial/manual_journals.html', journals=journals)

@financial_bp.route('/manual-journals/create', methods=['GET', 'POST'])
@login_required
def create_manual_journal():
    """Create new manual journal entry"""
    if request.method == 'POST':
        try:
            # Get form data
            reference = request.form.get('reference', '')
            date_str = request.form.get('date')
            description = request.form.get('description', '')
            
            # Parse date
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Generate entry number
            last_entry = JournalEntry.query.filter(
                JournalEntry.organization_id == current_user.organization_id,
                JournalEntry.entry_number.like('MJ%')
            ).order_by(JournalEntry.id.desc()).first()
            
            if last_entry:
                last_num = int(last_entry.entry_number[2:])
                entry_number = f"MJ{last_num + 1:06d}"
            else:
                entry_number = "MJ000001"
            
            # Create journal entry
            journal = JournalEntry(
                entry_number=entry_number,
                reference=reference,
                date=entry_date,
                description=description,
                source_type='manual',
                organization_id=current_user.organization_id,
                created_by=current_user.id
            )
            
            # Process line items
            line_items_data = request.form.getlist('line_items')
            debit_total = Decimal('0.00')
            credit_total = Decimal('0.00')
            
            for i, line_data in enumerate(line_items_data):
                if not line_data:
                    continue
                    
                account_id = request.form.get(f'account_id_{i}')
                description = request.form.get(f'line_description_{i}', '')
                debit = Decimal(request.form.get(f'debit_{i}', '0') or '0')
                credit = Decimal(request.form.get(f'credit_{i}', '0') or '0')
                
                if account_id and (debit > 0 or credit > 0):
                    line_item = JournalLineItem(
                        account_id=int(account_id),
                        description=description,
                        debit=debit,
                        credit=credit
                    )
                    journal.line_items.append(line_item)
                    debit_total += debit
                    credit_total += credit
            
            # Validate balanced entry
            if debit_total != credit_total:
                flash(f'Journal entry is not balanced. Debits: {debit_total}, Credits: {credit_total}', 'error')
                return redirect(url_for('financial.create_manual_journal'))
            
            journal.debit_total = debit_total
            journal.credit_total = credit_total
            
            db.session.add(journal)
            db.session.commit()
            
            # Update account balances
            for line_item in journal.line_items:
                account = Account.query.get(line_item.account_id)
                if account:
                    balance_change = line_item.debit - line_item.credit
                    account.current_balance = (account.current_balance or 0) + balance_change
            
            db.session.commit()
            
            flash('Manual journal entry created successfully!', 'success')
            return redirect(url_for('financial.manual_journals'))
            
        except Exception as e:
            flash(f'Error creating journal entry: {str(e)}', 'error')
            db.session.rollback()
    
    # Get all accounts for the form
    accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.is_active == True
    ).order_by(Account.code).all()
    
    return render_template('financial/create_manual_journal.html', accounts=accounts)

@financial_bp.route('/manual-journals/<int:id>')
@login_required
def view_manual_journal(id):
    """View manual journal entry details"""
    journal = JournalEntry.query.filter(
        JournalEntry.id == id,
        JournalEntry.organization_id == current_user.organization_id
    ).first_or_404()
    
    return render_template('financial/view_manual_journal.html', journal=journal)

@financial_bp.route('/reconciliation')
@login_required
def reconciliation():
    """Bank reconciliation dashboard"""
    # Get bank accounts
    bank_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        or_(
            Account.name.ilike('%bank%'),
            Account.name.ilike('%checking%'),
            Account.name.ilike('%savings%')
        ),
        Account.is_active == True
    ).all()
    
    return render_template('financial/reconciliation.html', accounts=bank_accounts)

@financial_bp.route('/reconciliation/<int:account_id>')
@login_required
def reconcile_account(account_id):
    """Bank reconciliation for specific account"""
    account = Account.query.filter(
        Account.id == account_id,
        Account.organization_id == current_user.organization_id
    ).first_or_404()
    
    # Get unreconciled transactions for this account
    transactions = db.session.query(JournalLineItem).join(JournalEntry).filter(
        JournalLineItem.account_id == account_id,
        JournalEntry.organization_id == current_user.organization_id
    ).order_by(JournalEntry.date.desc()).limit(100).all()
    
    return render_template('financial/reconcile_account.html', 
                         account=account, 
                         transactions=transactions)

@financial_bp.route('/cash-flow')
@login_required
def cash_flow():
    """Cash flow management and forecasting"""
    # Get cash accounts
    cash_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        or_(
            Account.name.ilike('%cash%'),
            Account.name.ilike('%bank%')
        ),
        Account.is_active == True
    ).all()
    
    # Calculate monthly cash flow for last 6 months
    six_months_ago = date.today() - timedelta(days=180)
    
    monthly_flow = db.session.query(
        func.date_trunc('month', JournalEntry.date).label('month'),
        func.sum(JournalLineItem.debit - JournalLineItem.credit).label('net_flow')
    ).join(JournalLineItem).filter(
        JournalEntry.organization_id == current_user.organization_id,
        JournalEntry.date >= six_months_ago,
        JournalLineItem.account_id.in_([acc.id for acc in cash_accounts])
    ).group_by(func.date_trunc('month', JournalEntry.date)).all()
    
    cash_flow_data = {
        'accounts': cash_accounts,
        'monthly_flow': monthly_flow,
        'total_cash': sum(acc.current_balance or 0 for acc in cash_accounts)
    }
    
    return render_template('financial/cash_flow.html', data=cash_flow_data)

# API endpoints for AJAX calls
@financial_bp.route('/api/account-balance/<int:account_id>')
@login_required
def get_account_balance(account_id):
    """Get current account balance via API"""
    account = Account.query.filter(
        Account.id == account_id,
        Account.organization_id == current_user.organization_id
    ).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify({
        'id': account.id,
        'name': account.name,
        'current_balance': float(account.current_balance or 0),
        'type': account.type.value
    })
