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

accounts_bp = Blueprint('accounts', __name__)

class AccountForm(FlaskForm):
    """Form for creating and editing accounts."""
    code = StringField('Account Code', validators=[DataRequired(), Length(min=1, max=20)])
    name = StringField('Account Name', validators=[DataRequired(), Length(min=1, max=255)])
    type = SelectField('Account Type', choices=[
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('accounts-receivable', 'Accounts Receivable'),
        ('inventory', 'Inventory'),
        ('other-current-asset', 'Other Current Asset'),
        ('fixed-asset', 'Fixed Asset'),
        ('non-current-asset', 'Non-Current Asset'),
        ('accounts-payable', 'Accounts Payable'),
        ('credit-card', 'Credit Card'),
        ('tax-payable', 'Tax Payable'),
        ('other-current-liability', 'Other Current Liability'),
        ('long-term-liability', 'Long Term Liability'),
        ('non-current-liability', 'Non-Current Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('other-income', 'Other Income'),
        ('cost-of-goods-sold', 'Cost of Goods Sold'),
        ('expense', 'Expense'),
        ('other-expense', 'Other Expense')
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
    # Placeholder data for now. You'll replace this with actual database queries.
    # Using predefined accounts from React version
    accounts = [
        # Assets
        {'id': 1, 'code': '10001', 'name': 'Bank Account', 'type': 'bank', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 2, 'code': '10002', 'name': 'Saving Bank Account', 'type': 'bank', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': False},
        {'id': 3, 'code': '10003', 'name': 'Undeposited Funds', 'type': 'cash', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 4, 'code': '10004', 'name': 'Petty Cash', 'type': 'cash', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 5, 'code': '10005', 'name': 'Computer Equipment', 'type': 'fixed-asset', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': False},
        {'id': 6, 'code': '10006', 'name': 'Office Equipment', 'type': 'fixed-asset', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': False},
        {'id': 7, 'code': '10007', 'name': 'Accounts Receivable (A/R)', 'type': 'accounts-receivable', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 8, 'code': '10008', 'name': 'Inventory Asset', 'type': 'inventory', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'An account that holds valuation of products or goods that available for sale.', 'predefined': True},
        {'id': 9, 'code': '100010', 'name': 'Prepaid Expenses', 'type': 'other-current-asset', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 10, 'code': '100020', 'name': 'Stripe Clearing', 'type': 'other-current-asset', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        
        # Liabilities
        {'id': 11, 'code': '20001', 'name': 'Accounts Payable (A/P)', 'type': 'accounts-payable', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 12, 'code': '20002', 'name': 'Owner A Drawings', 'type': 'other-current-liability', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'Withdrawals by the owners.', 'predefined': False},
        {'id': 13, 'code': '20003', 'name': 'Loan', 'type': 'other-current-liability', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'Money that has been borrowed from a creditor.', 'predefined': False},
        {'id': 14, 'code': '20004', 'name': 'Opening Balance Liabilities', 'type': 'other-current-liability', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'This account will hold the difference in the debits and credits entered during the opening balance.', 'predefined': False},
        {'id': 15, 'code': '20005', 'name': 'Revenue Received in Advance', 'type': 'other-current-liability', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'When customers pay in advance for products/services.', 'predefined': False},
        {'id': 16, 'code': '20006', 'name': 'Tax Payable', 'type': 'tax-payable', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        
        # Equity
        {'id': 17, 'code': '30001', 'name': 'Retained Earnings', 'type': 'equity', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'Retained earnings tracks net income from previous fiscal years.', 'predefined': True},
        {'id': 18, 'code': '30002', 'name': 'Opening Balance Equity', 'type': 'equity', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'When you enter opening balances to the accounts, the amounts enter in Opening balance equity. This ensures that you have a correct trial balance sheet for your company, without even specific the second credit or debit entry.', 'predefined': True},
        {'id': 19, 'code': '30003', 'name': "Owner's Equity", 'type': 'equity', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        
        # Expenses
        {'id': 20, 'code': '40001', 'name': 'Other Expenses', 'type': 'other-expense', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 21, 'code': '40002', 'name': 'Cost of Goods Sold', 'type': 'cost-of-goods-sold', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'Tracks the direct cost of the goods sold.', 'predefined': True},
        {'id': 22, 'code': '40003', 'name': 'Office expenses', 'type': 'expense', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': False},
        {'id': 23, 'code': '40004', 'name': 'Rent', 'type': 'expense', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': False},
        {'id': 24, 'code': '40005', 'name': 'Exchange Gain or Loss', 'type': 'other-expense', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'Tracks the gain and losses of the exchange differences.', 'predefined': True},
        {'id': 25, 'code': '40006', 'name': 'Bank Fees and Charges', 'type': 'expense', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'Any bank fees levied is recorded into the bank fees and charges account. A bank account maintenance fee, transaction charges, a late payment fee are some examples.', 'predefined': False},
        {'id': 26, 'code': '40007', 'name': 'Depreciation Expense', 'type': 'expense', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': False},
        {'id': 27, 'code': '40008', 'name': 'Discount', 'type': 'other-income', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 28, 'code': '40009', 'name': 'Purchase Discount', 'type': 'other-expense', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 29, 'code': '40010', 'name': 'Other Charges', 'type': 'other-income', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 30, 'code': '40011', 'name': 'Other Expenses', 'type': 'other-expense', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        
        # Income
        {'id': 31, 'code': '50001', 'name': 'Sales of Product Income', 'type': 'income', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 32, 'code': '50002', 'name': 'Sales of Service Income', 'type': 'income', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': False},
        {'id': 33, 'code': '50003', 'name': 'Uncategorized Income', 'type': 'income', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
        {'id': 34, 'code': '50004', 'name': 'Other Income', 'type': 'other-income', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': 'The income activities are not associated to the core business.', 'predefined': False},
        {'id': 35, 'code': '50005', 'name': 'Unearned Revenue', 'type': 'other-current-liability', 'balance': 0.00, 'parent_id': None, 'is_active': True, 'description': '', 'predefined': True},
    ]

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
