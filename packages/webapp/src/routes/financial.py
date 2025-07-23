"""
Financial routes for BigCapitalPy
Banking, Manual Journals, Reconciliation, and other financial operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, or_
import csv
import io
import os
from werkzeug.utils import secure_filename

from packages.server.src.models import (
    Account, AccountType, JournalEntry, JournalLineItem, 
    Customer, Vendor, Invoice, User, BankTransaction, 
    BankReconciliation, ReconciliationMatch
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
    
    return render_template('financial/create_manual_journal.html', 
                         accounts=accounts,
                         today=date.today())

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
    # Get bank accounts with their last reconciliation date
    bank_accounts = db.session.query(Account).outerjoin(BankReconciliation).filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        or_(
            Account.name.ilike('%bank%'),
            Account.name.ilike('%checking%'),
            Account.name.ilike('%savings%')
        ),
        Account.is_active == True
    ).all()
    
    # Get reconciliation stats for each account
    reconciliation_stats = {}
    for account in bank_accounts:
        last_reconciliation = BankReconciliation.query.filter_by(
            account_id=account.id,
            status='completed'
        ).order_by(BankReconciliation.statement_ending_date.desc()).first()
        
        unmatched_transactions = BankTransaction.query.filter_by(
            account_id=account.id,
            status='unmatched'
        ).count()
        
        reconciliation_stats[account.id] = {
            'last_reconciliation': last_reconciliation,
            'unmatched_count': unmatched_transactions
        }
    
    return render_template('financial/reconciliation.html', 
                         accounts=bank_accounts,
                         stats=reconciliation_stats)

@financial_bp.route('/reconciliation/start/<int:account_id>')
@login_required  
def start_reconciliation(account_id):
    """Start a new reconciliation for an account"""
    account = Account.query.filter(
        Account.id == account_id,
        Account.organization_id == current_user.organization_id
    ).first_or_404()
    
    # Check if there's an active reconciliation for this account
    active_reconciliation = BankReconciliation.query.filter_by(
        account_id=account_id,
        status='in_progress'
    ).first()
    
    if active_reconciliation:
        return redirect(url_for('financial.reconcile_account', 
                              reconciliation_id=active_reconciliation.id))
    
    return render_template('financial/start_reconciliation.html', account=account)

@financial_bp.route('/reconciliation/upload/<int:account_id>', methods=['GET', 'POST'])
@login_required
def upload_bank_statement(account_id):
    """Upload and import bank statement CSV"""
    account = Account.query.filter(
        Account.id == account_id,
        Account.organization_id == current_user.organization_id
    ).first_or_404()
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'bank_statement' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['bank_statement']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.csv'):
            try:
                # Read CSV file
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_input = csv.DictReader(stream)
                
                # Get form data for column mapping
                date_col = request.form.get('date_column')
                desc_col = request.form.get('description_column')
                amount_col = request.form.get('amount_column')
                ref_col = request.form.get('reference_column', '')
                balance_col = request.form.get('balance_column', '')
                
                imported_count = 0
                duplicate_count = 0
                
                for row in csv_input:
                    try:
                        # Parse transaction data
                        transaction_date = datetime.strptime(row[date_col], '%Y-%m-%d').date()
                        description = row[desc_col]
                        amount = Decimal(str(row[amount_col]))
                        reference = row.get(ref_col, '') if ref_col else ''
                        balance = Decimal(str(row[balance_col])) if balance_col and row.get(balance_col) else None
                        
                        # Check for duplicates
                        existing = BankTransaction.query.filter_by(
                            account_id=account_id,
                            transaction_date=transaction_date,
                            description=description,
                            amount=amount
                        ).first()
                        
                        if existing:
                            duplicate_count += 1
                            continue
                        
                        # Create bank transaction
                        bank_transaction = BankTransaction(
                            account_id=account_id,
                            transaction_date=transaction_date,
                            description=description,
                            reference=reference,
                            amount=amount,
                            balance=balance,
                            organization_id=current_user.organization_id
                        )
                        
                        db.session.add(bank_transaction)
                        imported_count += 1
                        
                    except (ValueError, KeyError) as e:
                        flash(f'Error processing row: {str(e)}', 'warning')
                        continue
                
                db.session.commit()
                
                flash(f'Successfully imported {imported_count} transactions. '
                      f'{duplicate_count} duplicates were skipped.', 'success')
                
                return redirect(url_for('financial.start_reconciliation', account_id=account_id))
                
            except Exception as e:
                flash(f'Error processing CSV file: {str(e)}', 'error')
                db.session.rollback()
        else:
            flash('Please upload a CSV file', 'error')
    
    return render_template('financial/upload_statement.html', account=account)

@financial_bp.route('/reconciliation/create/<int:account_id>', methods=['POST'])
@login_required
def create_reconciliation(account_id):
    """Create a new reconciliation session"""
    account = Account.query.filter(
        Account.id == account_id,
        Account.organization_id == current_user.organization_id
    ).first_or_404()
    
    try:
        statement_date = datetime.strptime(request.form.get('statement_date'), '%Y-%m-%d').date()
        statement_balance = Decimal(request.form.get('statement_balance'))
        
        # Calculate book balance up to statement date
        book_balance = account.current_balance or Decimal('0.00')
        
        # Create reconciliation
        reconciliation = BankReconciliation(
            account_id=account_id,
            reconciliation_date=date.today(),
            statement_ending_date=statement_date,
            statement_ending_balance=statement_balance,
            book_ending_balance=book_balance,
            difference=book_balance - statement_balance,
            organization_id=current_user.organization_id,
            created_by=current_user.id
        )
        
        db.session.add(reconciliation)
        db.session.commit()
        
        flash('Reconciliation started successfully!', 'success')
        return redirect(url_for('financial.reconcile_account', 
                              reconciliation_id=reconciliation.id))
        
    except Exception as e:
        flash(f'Error starting reconciliation: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('financial.start_reconciliation', account_id=account_id))

@financial_bp.route('/reconciliation/<int:reconciliation_id>')
@login_required
def reconcile_account(reconciliation_id):
    """Bank reconciliation workspace"""
    reconciliation = BankReconciliation.query.filter(
        BankReconciliation.id == reconciliation_id,
        BankReconciliation.organization_id == current_user.organization_id
    ).first_or_404()
    
    # Get unmatched bank transactions up to statement date
    bank_transactions = BankTransaction.query.filter(
        BankTransaction.account_id == reconciliation.account_id,
        BankTransaction.transaction_date <= reconciliation.statement_ending_date,
        BankTransaction.status == 'unmatched'
    ).order_by(BankTransaction.transaction_date.desc()).all()
    
    # Get unreconciled journal entries for this account up to statement date
    journal_entries = db.session.query(JournalLineItem).join(JournalEntry).filter(
        JournalLineItem.account_id == reconciliation.account_id,
        JournalEntry.date <= reconciliation.statement_ending_date,
        JournalEntry.organization_id == current_user.organization_id,
        ~JournalLineItem.id.in_(
            db.session.query(ReconciliationMatch.journal_line_item_id).filter(
                ReconciliationMatch.journal_line_item_id.isnot(None)
            )
        )
    ).order_by(JournalEntry.date.desc()).all()
    
    # Get existing matches for this reconciliation
    matches = ReconciliationMatch.query.filter_by(
        reconciliation_id=reconciliation_id
    ).all()
    
    # Calculate reconciliation summary
    matched_bank_total = sum(
        match.bank_transaction.amount 
        for match in matches 
        if match.bank_transaction
    )
    matched_journal_total = sum(
        (match.journal_line_item.debit or 0) - (match.journal_line_item.credit or 0)
        for match in matches 
        if match.journal_line_item
    )
    
    # Get all active accounts for contra account selection
    all_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.is_active == True,
        Account.id != reconciliation.account_id
    ).order_by(Account.code).all()
    
    reconciliation_data = {
        'reconciliation': reconciliation,
        'bank_transactions': bank_transactions,
        'journal_entries': journal_entries,
        'matches': matches,
        'matched_bank_total': matched_bank_total,
        'matched_journal_total': matched_journal_total,
        'remaining_difference': reconciliation.difference - matched_bank_total + matched_journal_total,
        'accounts': all_accounts
    }
    
    return render_template('financial/reconcile_account.html', data=reconciliation_data)

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
        func.strftime('%Y-%m', JournalEntry.date).label('month'),
        func.sum(JournalLineItem.debit - JournalLineItem.credit).label('net_flow')
    ).join(JournalLineItem).filter(
        JournalEntry.organization_id == current_user.organization_id,
        JournalEntry.date >= six_months_ago,
        JournalLineItem.account_id.in_([acc.id for acc in cash_accounts])
    ).group_by(func.strftime('%Y-%m', JournalEntry.date)).all()
    
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

@financial_bp.route('/reconciliation/<int:reconciliation_id>/match', methods=['POST'])
@login_required
def match_transactions(reconciliation_id):
    """Match bank transaction with journal entry"""
    reconciliation = BankReconciliation.query.filter(
        BankReconciliation.id == reconciliation_id,
        BankReconciliation.organization_id == current_user.organization_id
    ).first_or_404()
    
    try:
        bank_transaction_id = request.form.get('bank_transaction_id')
        journal_line_item_id = request.form.get('journal_line_item_id')
        
        # Create the match
        match = ReconciliationMatch(
            reconciliation_id=reconciliation_id,
            bank_transaction_id=int(bank_transaction_id) if bank_transaction_id else None,
            journal_line_item_id=int(journal_line_item_id) if journal_line_item_id else None,
            match_type='manual'
        )
        
        db.session.add(match)
        
        # Update bank transaction status if matched
        if bank_transaction_id:
            bank_transaction = BankTransaction.query.get(bank_transaction_id)
            if bank_transaction:
                bank_transaction.status = 'matched'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Transactions matched successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@financial_bp.route('/reconciliation/<int:reconciliation_id>/unmatch/<int:match_id>', methods=['POST'])
@login_required
def unmatch_transaction(reconciliation_id, match_id):
    """Remove a transaction match"""
    match = ReconciliationMatch.query.filter(
        ReconciliationMatch.id == match_id,
        ReconciliationMatch.reconciliation_id == reconciliation_id
    ).first_or_404()
    
    try:
        # Update bank transaction status if it was matched
        if match.bank_transaction:
            match.bank_transaction.status = 'unmatched'
        
        db.session.delete(match)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Match removed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@financial_bp.route('/reconciliation/<int:reconciliation_id>/auto-match', methods=['POST'])
@login_required
def auto_match_transactions(reconciliation_id):
    """Automatically match transactions based on date and amount"""
    reconciliation = BankReconciliation.query.filter(
        BankReconciliation.id == reconciliation_id,
        BankReconciliation.organization_id == current_user.organization_id
    ).first_or_404()
    
    try:
        matched_count = 0
        
        # Get unmatched bank transactions
        bank_transactions = BankTransaction.query.filter(
            BankTransaction.account_id == reconciliation.account_id,
            BankTransaction.transaction_date <= reconciliation.statement_ending_date,
            BankTransaction.status == 'unmatched'
        ).all()
        
        for bank_txn in bank_transactions:
            # Look for journal entries with same date and amount
            matching_journal = db.session.query(JournalLineItem).join(JournalEntry).filter(
                JournalLineItem.account_id == reconciliation.account_id,
                JournalEntry.date == bank_txn.transaction_date,
                or_(
                    and_(bank_txn.amount > 0, JournalLineItem.debit == bank_txn.amount),
                    and_(bank_txn.amount < 0, JournalLineItem.credit == abs(bank_txn.amount))
                ),
                ~JournalLineItem.id.in_(
                    db.session.query(ReconciliationMatch.journal_line_item_id).filter(
                        ReconciliationMatch.journal_line_item_id.isnot(None)
                    )
                )
            ).first()
            
            if matching_journal:
                # Create automatic match
                match = ReconciliationMatch(
                    reconciliation_id=reconciliation_id,
                    bank_transaction_id=bank_txn.id,
                    journal_line_item_id=matching_journal.id,
                    match_type='automatic',
                    confidence_score=1.0
                )
                
                db.session.add(match)
                bank_txn.status = 'matched'
                matched_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Automatically matched {matched_count} transactions',
            'matched_count': matched_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@financial_bp.route('/reconciliation/<int:reconciliation_id>/create-entry', methods=['POST'])
@login_required
def create_journal_entry_from_bank(reconciliation_id):
    """Create a journal entry from an unmatched bank transaction"""
    reconciliation = BankReconciliation.query.filter(
        BankReconciliation.id == reconciliation_id,
        BankReconciliation.organization_id == current_user.organization_id
    ).first_or_404()
    
    try:
        bank_transaction_id = request.form.get('bank_transaction_id')
        contra_account_id = request.form.get('contra_account_id')
        description = request.form.get('description')
        
        bank_txn = BankTransaction.query.get(bank_transaction_id)
        if not bank_txn:
            return jsonify({'success': False, 'message': 'Bank transaction not found'}), 404
        
        # Generate entry number
        last_entry = JournalEntry.query.filter(
            JournalEntry.organization_id == current_user.organization_id,
            JournalEntry.entry_number.like('BANK%')
        ).order_by(JournalEntry.id.desc()).first()
        
        if last_entry:
            last_num = int(last_entry.entry_number[4:])
            entry_number = f"BANK{last_num + 1:06d}"
        else:
            entry_number = "BANK000001"
        
        # Create journal entry
        journal = JournalEntry(
            entry_number=entry_number,
            reference=bank_txn.reference or '',
            date=bank_txn.transaction_date,
            description=description or bank_txn.description,
            source_type='bank_reconciliation',
            organization_id=current_user.organization_id,
            created_by=current_user.id
        )
        
        # Create line items
        if bank_txn.amount > 0:  # Deposit
            # Debit bank account
            bank_line = JournalLineItem(
                account_id=bank_txn.account_id,
                description=description or bank_txn.description,
                debit=bank_txn.amount,
                credit=Decimal('0.00')
            )
            # Credit contra account
            contra_line = JournalLineItem(
                account_id=int(contra_account_id),
                description=description or bank_txn.description,
                debit=Decimal('0.00'),
                credit=bank_txn.amount
            )
        else:  # Withdrawal
            # Credit bank account
            bank_line = JournalLineItem(
                account_id=bank_txn.account_id,
                description=description or bank_txn.description,
                debit=Decimal('0.00'),
                credit=abs(bank_txn.amount)
            )
            # Debit contra account
            contra_line = JournalLineItem(
                account_id=int(contra_account_id),
                description=description or bank_txn.description,
                debit=abs(bank_txn.amount),
                credit=Decimal('0.00')
            )
        
        journal.line_items.extend([bank_line, contra_line])
        journal.debit_total = abs(bank_txn.amount)
        journal.credit_total = abs(bank_txn.amount)
        
        db.session.add(journal)
        db.session.flush()  # Get the journal ID
        
        # Create match between bank transaction and journal entry
        match = ReconciliationMatch(
            reconciliation_id=reconciliation_id,
            bank_transaction_id=bank_txn.id,
            journal_line_item_id=bank_line.id,
            match_type='created'
        )
        
        db.session.add(match)
        bank_txn.status = 'matched'
        
        # Update account balances
        bank_account = Account.query.get(bank_txn.account_id)
        contra_account = Account.query.get(contra_account_id)
        
        if bank_account:
            bank_account.current_balance = (bank_account.current_balance or 0) + bank_txn.amount
        
        if contra_account:
            contra_balance_change = -bank_txn.amount if bank_txn.amount > 0 else abs(bank_txn.amount)
            contra_account.current_balance = (contra_account.current_balance or 0) + contra_balance_change
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Journal entry created and matched successfully',
            'journal_id': journal.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@financial_bp.route('/reconciliation/<int:reconciliation_id>/complete', methods=['POST'])
@login_required
def complete_reconciliation(reconciliation_id):
    """Complete the reconciliation if balanced"""
    reconciliation = BankReconciliation.query.filter(
        BankReconciliation.id == reconciliation_id,
        BankReconciliation.organization_id == current_user.organization_id
    ).first_or_404()
    
    try:
        # Calculate final difference
        matches = ReconciliationMatch.query.filter_by(reconciliation_id=reconciliation_id).all()
        
        matched_bank_total = sum(
            match.bank_transaction.amount 
            for match in matches 
            if match.bank_transaction
        )
        
        final_difference = reconciliation.statement_ending_balance - (reconciliation.book_ending_balance + matched_bank_total)
        
        if abs(final_difference) < 0.01:  # Allow for rounding differences
            reconciliation.status = 'completed'
            reconciliation.difference = final_difference
            reconciliation.updated_at = datetime.utcnow()
            
            # Mark all matched bank transactions as reconciled
            for match in matches:
                if match.bank_transaction:
                    match.bank_transaction.status = 'reconciled'
            
            db.session.commit()
            
            flash('Reconciliation completed successfully!', 'success')
            return redirect(url_for('financial.reconciliation'))
        else:
            flash(f'Reconciliation is not balanced. Difference: {final_difference}', 'error')
            return redirect(url_for('financial.reconcile_account', reconciliation_id=reconciliation_id))
            
    except Exception as e:
        flash(f'Error completing reconciliation: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('financial.reconcile_account', reconciliation_id=reconciliation_id))

@financial_bp.route('/reconciliation/<int:reconciliation_id>/discard', methods=['POST'])
@login_required
def discard_reconciliation(reconciliation_id):
    """Discard the reconciliation and reset transaction statuses"""
    reconciliation = BankReconciliation.query.filter(
        BankReconciliation.id == reconciliation_id,
        BankReconciliation.organization_id == current_user.organization_id
    ).first_or_404()
    
    try:
        # Reset bank transaction statuses
        matches = ReconciliationMatch.query.filter_by(reconciliation_id=reconciliation_id).all()
        for match in matches:
            if match.bank_transaction:
                match.bank_transaction.status = 'unmatched'
        
        # Delete all matches
        ReconciliationMatch.query.filter_by(reconciliation_id=reconciliation_id).delete()
        
        # Mark reconciliation as discarded
        reconciliation.status = 'discarded'
        reconciliation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Reconciliation discarded successfully', 'info')
        return redirect(url_for('financial.reconciliation'))
        
    except Exception as e:
        flash(f'Error discarding reconciliation: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('financial.reconcile_account', reconciliation_id=reconciliation_id))
