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
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense')
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
    accounts = [
        {'id': 1, 'code': '1000', 'name': 'Cash on Hand', 'type': 'asset', 'balance': 1500.00, 'parent_id': None},
        {'id': 2, 'code': '4000', 'name': 'Sales Revenue', 'type': 'income', 'balance': 10000.00, 'parent_id': None},
    ]

    class Summary:
        def __init__(self, count=0, balance=0):
            self.count = count
            self.balance = balance

    account_summary = type('AccountSummary', (), {})()
    account_summary.assets = Summary(count=1, balance=1500.00)
    account_summary.liabilities = Summary(count=0, balance=0)
    account_summary.equity = Summary(count=0, balance=0)
    account_summary.income = Summary(count=1, balance=10000.00)
    account_summary.expense = Summary(count=0, balance=0)

    # Group accounts by type for template (robust fallback)
    accounts_by_type = {
        'asset': [a for a in accounts if a['type'] == 'asset'],
        'liability': [a for a in accounts if a['type'] == 'liability'],
        'equity': [a for a in accounts if a['type'] == 'equity'],
        'income': [a for a in accounts if a['type'] == 'income'],
        'expense': [a for a in accounts if a['type'] == 'expense'],
    }

    # Pass the macro to the template context for recursive rendering
    return render_template('accounts/index.html', accounts=accounts, account_summary=account_summary, accounts_by_type=accounts_by_type, render_account_tree=None)

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
