"""
Banking routes for BigCapitalPy
Bank accounts management, transactions, and reconciliation
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Length, Optional
from packages.server.src.models import BankAccount, BankTransaction, db
from datetime import datetime
import csv
import io

banking_bp = Blueprint('banking', __name__, url_prefix='/banking')

class BankAccountForm(FlaskForm):
    """Form for creating and editing bank accounts."""
    name = StringField('Account Name', validators=[DataRequired(), Length(min=1, max=255)])
    account_number = StringField('Account Number', validators=[Optional(), Length(max=100)])
    account_type = SelectField('Account Type', choices=[
        ('cash', 'Cash'),
        ('bank', 'Bank Account'),
        ('credit-card', 'Credit Card')
    ], validators=[DataRequired()])
    balance = DecimalField('Current Balance', places=2, validators=[Optional()])
    currency = StringField('Currency', default='USD', validators=[Optional(), Length(max=3)])
    is_active = BooleanField('Active', default=True)

@banking_bp.route('/accounts')
@login_required
def accounts():
    """List all bank accounts"""
    bank_accounts = BankAccount.query.filter_by(
        organization_id=current_user.organization_id
    ).all()
    
    return render_template('banking/accounts.html', accounts=bank_accounts)

@banking_bp.route('/accounts/new', methods=['GET', 'POST'])
@login_required
def new_account():
    """Create a new bank account"""
    form = BankAccountForm()
    
    if form.validate_on_submit():
        bank_account = BankAccount(
            name=form.name.data,
            account_number=form.account_number.data,
            account_type=form.account_type.data,
            balance=form.balance.data or 0,
            currency=form.currency.data,
            is_active=form.is_active.data,
            organization_id=current_user.organization_id
        )
        
        db.session.add(bank_account)
        db.session.commit()
        
        flash('Bank account created successfully!', 'success')
        return redirect(url_for('banking.accounts'))
    
    return render_template('banking/new_account.html', form=form)

@banking_bp.route('/accounts/<int:account_id>')
@login_required
def account_detail(account_id):
    """View bank account details and transactions"""
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    # Get recent transactions
    transactions = BankTransaction.query.filter_by(
        account_id=account_id
    ).order_by(BankTransaction.transaction_date.desc()).limit(50).all()
    
    return render_template('banking/account_detail.html', 
                         account=bank_account, 
                         transactions=transactions)

# API endpoints for React frontend

@banking_bp.route('/api/accounts', methods=['GET'])
@login_required
def api_accounts():
    """API endpoint for bank accounts list"""
    bank_accounts = BankAccount.query.filter_by(
        organization_id=current_user.organization_id
    ).all()
    
    accounts_data = []
    for account in bank_accounts:
        accounts_data.append({
            'id': account.id,
            'name': account.name,
            'account_number': account.account_number,
            'account_type': account.account_type,
            'balance': float(account.balance) if account.balance else 0,
            'currency': account.currency,
            'is_active': account.is_active,
            'feeds_paused': account.feeds_paused,
            'created_at': account.created_at.isoformat() if account.created_at else None,
            'updated_at': account.updated_at.isoformat() if account.updated_at else None
        })
    
    return jsonify(accounts_data)

@banking_bp.route('/api/accounts', methods=['POST'])
@login_required
def api_create_account():
    """API endpoint for creating bank accounts"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'account_type' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    bank_account = BankAccount(
        name=data['name'],
        account_number=data.get('account_number'),
        account_type=data['account_type'],
        balance=data.get('balance', 0),
        currency=data.get('currency', 'USD'),
        is_active=data.get('is_active', True),
        organization_id=current_user.organization_id
    )
    
    db.session.add(bank_account)
    db.session.commit()
    
    return jsonify({
        'id': bank_account.id,
        'name': bank_account.name,
        'account_type': bank_account.account_type,
        'balance': float(bank_account.balance),
        'currency': bank_account.currency,
        'is_active': bank_account.is_active
    }), 201

@banking_bp.route('/api/accounts/<int:account_id>', methods=['PUT'])
@login_required
def api_update_account(account_id):
    """API endpoint for updating bank accounts"""
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'name' in data:
        bank_account.name = data['name']
    if 'account_number' in data:
        bank_account.account_number = data['account_number']
    if 'account_type' in data:
        bank_account.account_type = data['account_type']
    if 'balance' in data:
        bank_account.balance = data['balance']
    if 'currency' in data:
        bank_account.currency = data['currency']
    if 'is_active' in data:
        bank_account.is_active = data['is_active']
    
    bank_account.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'id': bank_account.id,
        'name': bank_account.name,
        'account_type': bank_account.account_type,
        'balance': float(bank_account.balance),
        'currency': bank_account.currency,
        'is_active': bank_account.is_active
    })

@banking_bp.route('/api/accounts/<int:account_id>/pause', methods=['POST'])
@login_required
def api_pause_feeds(account_id):
    """API endpoint to pause feeds for a bank account"""
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    bank_account.feeds_paused = True
    db.session.commit()
    
    return jsonify({'success': True})

@banking_bp.route('/accounts/<int:account_id>/import', methods=['GET', 'POST'])
@login_required
def import_transactions(account_id):
    """Import transactions for a bank account"""
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'csv_file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if not file.filename.lower().endswith('.csv'):
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
        
        try:
            # Read CSV content
            import csv
            import io
            
            # Decode file content
            content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            
            transactions_imported = 0
            for row in csv_reader:
                try:
                    # Parse transaction data (similar to the import script)
                    transaction_date = datetime.strptime(row['parsed_date'], '%Y-%m-%d').date()
                    
                    # Determine amount
                    debit_str = row.get('debit_net_amount', '').strip()
                    credit_str = row.get('credit_net_amount', '').strip()
                    
                    debit_amount = float(debit_str.replace(',', '')) if debit_str else 0
                    credit_amount = float(credit_str.replace(',', '')) if credit_str else 0
                    
                    if debit_amount > 0:
                        amount = -debit_amount
                    elif credit_amount > 0:
                        amount = credit_amount
                    else:
                        continue  # Skip zero-amount transactions
                    
                    # Get description
                    description = row.get('description', '').strip()[:500]
                    if not description:
                        description = f"{row.get('type', 'Unknown')} transaction"
                    
                    # Get balance
                    balance_str = row.get('account_balance', '').strip()
                    balance = float(balance_str.replace(',', '')) if balance_str else 0
                    
                    # Check for duplicate
                    reference = row.get('transaction_id', '').strip()
                    if reference:
                        existing = BankTransaction.query.filter_by(
                            reference=reference,
                            account_id=account_id
                        ).first()
                        if existing:
                            continue
                    
                    # Create transaction
                    transaction = BankTransaction(
                        account_id=account_id,
                        transaction_date=transaction_date,
                        amount=amount,
                        description=description,
                        reference=reference,
                        balance=balance,
                        status='unmatched',
                        organization_id=current_user.organization_id
                    )
                    
                    db.session.add(transaction)
                    transactions_imported += 1
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
            
            # Update account balance
            if transactions_imported > 0:
                # Get the latest balance from the imported transactions
                latest_transaction = BankTransaction.query.filter_by(
                    account_id=account_id
                ).order_by(BankTransaction.transaction_date.desc()).first()
                if latest_transaction:
                    bank_account.balance = latest_transaction.balance
            
            db.session.commit()
            
            flash(f'Successfully imported {transactions_imported} transactions!', 'success')
            return redirect(url_for('banking.account_detail', account_id=account_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error importing transactions: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('banking/import_transactions.html', account=bank_account)