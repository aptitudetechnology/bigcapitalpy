"""
Accounts blueprint for BigCapitalPy.
Handles Chart of Accounts and related operations.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Length, Optional
# You'll likely need to import models and db here later
# from packages.server.src.models import Account, AccountType
# from packages.server.src.database import db
from packages.server.src.modules.Accounts.accounts_constants import ACCOUNT_TYPES, SEED_ACCOUNTS
from packages.server.src.modules.Accounts.accounts_constants import ACCOUNT_TYPES

accounts_bp = Blueprint('accounts', __name__)

class AccountForm(FlaskForm):
    """Form for creating and editing accounts."""
    code = StringField('Account Code', validators=[DataRequired(), Length(min=1, max=20)])
    name = StringField('Account Name', validators=[DataRequired(), Length(min=1, max=255)])
    type = SelectField('Account Type', choices=[
        (account_type['key'], account_type['label']) for account_type in ACCOUNT_TYPES
    ], validators=[DataRequired()])
    parent_id = SelectField('Parent Account', choices=[], validators=[Optional()], coerce=int)
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    opening_balance = DecimalField('Opening Balance', places=2, validators=[Optional()])
    is_active = BooleanField('Active', default=True)

@accounts_bp.route('/')
@login_required
def index():
    """
    Chart of Accounts listing page.
    """
    # Use predefined accounts from React version
    accounts = []
    for i, seed_account in enumerate(SEED_ACCOUNTS, 1):
        accounts.append({
            'id': i,
            'code': seed_account['code'],
            'name': seed_account['name'],
            'type': seed_account['account_type'],
            'balance': 0.00,  # Placeholder balance
            'parent_id': None,  # Placeholder parent
            'is_active': seed_account['active'],
            'description': seed_account['description'],
            'predefined': seed_account['predefined']
        })

    # Calculate account summary by type categories
    asset_types = ['bank', 'cash', 'accounts-receivable', 'inventory', 'fixed-asset', 'other-current-asset']
    liability_types = ['accounts-payable', 'tax-payable', 'other-current-liability']
    equity_types = ['equity']
    income_types = ['income', 'other-income']
    expense_types = ['expense', 'cost-of-goods-sold', 'other-expense']
    
    class Summary:
        def __init__(self, count=0, balance=0):
            self.count = count
            self.balance = balance

    account_summary = type('AccountSummary', (), {})()
    account_summary.assets = Summary(
        count=sum(1 for a in accounts if a['type'] in asset_types),
        balance=sum(a['balance'] for a in accounts if a['type'] in asset_types)
    )
    account_summary.liabilities = Summary(
        count=sum(1 for a in accounts if a['type'] in liability_types),
        balance=sum(a['balance'] for a in accounts if a['type'] in liability_types)
    )
    account_summary.equity = Summary(
        count=sum(1 for a in accounts if a['type'] in equity_types),
        balance=sum(a['balance'] for a in accounts if a['type'] in equity_types)
    )
    account_summary.income = Summary(
        count=sum(1 for a in accounts if a['type'] in income_types),
        balance=sum(a['balance'] for a in accounts if a['type'] in income_types)
    )
    account_summary.expense = Summary(
        count=sum(1 for a in accounts if a['type'] in expense_types),
        balance=sum(a['balance'] for a in accounts if a['type'] in expense_types)
    )

    # Group accounts by type for template (dynamic grouping by actual types)
    from collections import defaultdict
    accounts_by_type = defaultdict(list)
    for account in accounts:
        accounts_by_type[account['type']].append(account)

    # Pass the macro to the template context for recursive rendering
    return render_template('accounts/index.html', accounts=accounts, account_summary=account_summary, accounts_by_type=accounts_by_type)

@accounts_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """
    Create a new account (Chart of Accounts).
    """
    form = AccountForm()
    
    # Populate parent account choices (placeholder for now)
    form.parent_id.choices = [(0, '-- None --')]  # Add actual parent accounts later
    
    if form.validate_on_submit():
        # Here you would process form data and create the account
        flash('Account created successfully!', 'success')
        return redirect(url_for('accounts.index'))
    
    return render_template('accounts/new.html', form=form)

# Add other account-related routes as needed (e.g., /<int:id>, /edit, /delete)

@accounts_bp.route('/<int:account_id>')
@login_required
def show(account_id):
    """
    Show account details.
    """
    # Placeholder - find account by ID
    accounts = [
        {'id': 1, 'code': '1000', 'name': 'Cash on Hand', 'type': 'asset', 'balance': 1500.00, 'parent_id': None, 'is_active': True, 'description': 'Primary cash account', 'children': []},
        {'id': 2, 'code': '4000', 'name': 'Sales Revenue', 'type': 'income', 'balance': 10000.00, 'parent_id': None, 'is_active': True, 'description': 'Revenue from sales', 'children': []},
    ]
    
    account = next((a for a in accounts if a['id'] == account_id), None)
    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('accounts.index'))
    
    return render_template('accounts/show.html', account=account)
