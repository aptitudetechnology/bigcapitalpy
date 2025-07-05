"""
Chart of Accounts routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DecimalField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.widgets import NumberInput
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from packages.server.src.models import db, Account, AccountType
from collections import defaultdict

accounts_bp = Blueprint('accounts', __name__)


def coerce_parent_id(value):
    """Custom coerce function for parent_id SelectField.
    
    Handles empty strings (for 'No Parent' option) and converts valid integers.
    Returns None for empty values, integer for valid numeric values.
    """
    if not value or value == '':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


class AccountForm(FlaskForm):
    code = StringField('Account Code', validators=[DataRequired(), Length(min=1, max=20)])
    name = StringField('Account Name', validators=[DataRequired(), Length(min=1, max=255)])
    type = SelectField('Account Type', 
                      choices=[
                          ('asset', 'Asset'),
                          ('liability', 'Liability'),
                          ('equity', 'Equity'),
                          ('income', 'Income'),
                          ('expense', 'Expense')
                      ],
                      validators=[DataRequired()])
    parent_id = SelectField('Parent Account', coerce=coerce_parent_id, validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    opening_balance = DecimalField('Opening Balance', 
                                 default=0.00, 
                                 validators=[Optional(), NumberRange(min=-999999999.99, max=999999999.99)],
                                 widget=NumberInput(step='0.01'))
    is_active = BooleanField('Active', default=True)

    def __init__(self, account_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate parent account choices
        accounts = Account.query.filter_by(is_active=True).order_by(Account.name).all()
        choices = [('', 'No Parent')]
        for account in accounts:
            if account_id is None or account.id != account_id:  # Don't allow account to be its own parent
                choices.append((account.id, f"{account.code} - {account.name}"))
        self.parent_id.choices = choices

def build_account_tree(accounts):
    """Build a hierarchical tree structure from accounts"""
    account_dict = {account.id: account for account in accounts}
    root_accounts = []
    
    for account in accounts:
        if account.parent_id is None:
            root_accounts.append(account)
        else:
            parent = account_dict.get(account.parent_id)
            if parent:
                if not hasattr(parent, 'children_list'):
                    parent.children_list = []
                parent.children_list.append(account)
    
    return root_accounts

def get_account_summary(accounts):
    """Get summary statistics for accounts by type"""
    summary = {
        'asset': {'count': 0, 'balance': 0},
        'liability': {'count': 0, 'balance': 0},
        'equity': {'count': 0, 'balance': 0},
        'income': {'count': 0, 'balance': 0},
        'expense': {'count': 0, 'balance': 0}
    }
    
    for account in accounts:
        account_type = account.type.value
        if account_type in summary:
            summary[account_type]['count'] += 1
            summary[account_type]['balance'] += float(account.current_balance or 0)
    
    # Create an object-like structure for template access
    class AccountSummary:
        def __init__(self, data):
            # Map singular to plural forms for template compatibility
            self.assets = type('obj', (object,), data.get('asset', {'count': 0, 'balance': 0}))
            self.liabilities = type('obj', (object,), data.get('liability', {'count': 0, 'balance': 0}))
            self.equity = type('obj', (object,), data.get('equity', {'count': 0, 'balance': 0}))
            self.income = type('obj', (object,), data.get('income', {'count': 0, 'balance': 0}))
            self.expense = type('obj', (object,), data.get('expense', {'count': 0, 'balance': 0}))
    
    return AccountSummary(summary)

@accounts_bp.route('/')
@login_required
def index():
    """Display the chart of accounts"""
    # Get filter parameters
    search = request.args.get('search', '').strip()
    account_type_filter = request.args.get('type', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    # Build query with organization filter
    query = Account.query.filter(Account.organization_id == current_user.organization_id)
    
    if search:
        query = query.filter(
            db.or_(
                Account.name.ilike(f'%{search}%'),
                Account.code.ilike(f'%{search}%'),
                Account.description.ilike(f'%{search}%')
            )
        )
    
    if account_type_filter:
        try:
            query = query.filter(Account.type == AccountType(account_type_filter))
        except ValueError:
            flash(f'Invalid account type: {account_type_filter}', 'warning')
    
    if status_filter == 'active':
        query = query.filter(Account.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(Account.is_active == False)
    
    accounts = query.order_by(Account.code, Account.name).all()
    
    # Group accounts by type for tree view
    accounts_by_type = defaultdict(list)
    for account in accounts:
        accounts_by_type[account.type.value].append(account)
    
    # Get summary statistics
    account_summary = get_account_summary(accounts)
    
    return render_template('accounts/index.html',
                         accounts=accounts,
                         accounts_by_type=dict(accounts_by_type),
                         account_summary=account_summary)

@accounts_bp.route('/new', methods=['GET', 'POST'])
def new():
    """Create a new account"""
    form = AccountForm()
    
    if form.validate_on_submit():
        # Check if account code already exists
        existing = Account.query.filter_by(code=form.code.data).first()
        if existing:
            flash('Account code already exists. Please choose a different code.', 'error')
            return render_template('accounts/new.html', form=form)
        
        account = Account(
            code=form.code.data,
            name=form.name.data,
            type=AccountType(form.type.data),
            parent_id=form.parent_id.data or None,
            description=form.description.data,
            opening_balance=form.opening_balance.data or 0,
            current_balance=form.opening_balance.data or 0,
            is_active=form.is_active.data,
            organization_id=1  # TODO: Get from session
        )
        
        try:
            db.session.add(account)
            db.session.commit()
            flash(f'Account "{account.name}" has been created successfully.', 'success')
            return redirect(url_for('accounts.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the account. Please try again.', 'error')
    
    return render_template('accounts/new.html', form=form)

@accounts_bp.route('/<int:account_id>')
def show(account_id):
    """Display account details"""
    account = Account.query.get_or_404(account_id)
    
    # Get child accounts
    children = Account.query.filter_by(parent_id=account_id).order_by(Account.code).all()
    
    return render_template('accounts/show.html', account=account, children=children)

@accounts_bp.route('/<int:account_id>/edit', methods=['GET', 'POST'])
def edit(account_id):
    """Edit an existing account"""
    account = Account.query.get_or_404(account_id)
    form = AccountForm(account_id=account_id)
    
    if form.validate_on_submit():
        # Check if account code already exists (excluding current account)
        existing = Account.query.filter(
            Account.code == form.code.data,
            Account.id != account_id
        ).first()
        if existing:
            flash('Account code already exists. Please choose a different code.', 'error')
            return render_template('accounts/edit.html', form=form, account=account)
        
        # Check for circular parent relationship
        if form.parent_id.data:
            parent_id = form.parent_id.data
            visited = set()
            while parent_id:
                if parent_id == account_id:
                    flash('Cannot set parent account - this would create a circular reference.', 'error')
                    return render_template('accounts/edit.html', form=form, account=account)
                if parent_id in visited:
                    break
                visited.add(parent_id)
                parent_account = Account.query.get(parent_id)
                parent_id = parent_account.parent_id if parent_account else None
        
        account.code = form.code.data
        account.name = form.name.data
        account.type = AccountType(form.type.data)
        account.parent_id = form.parent_id.data or None
        account.description = form.description.data
        account.is_active = form.is_active.data
        
        # Only update opening balance if it's different (to preserve transaction history)
        if form.opening_balance.data != account.opening_balance:
            balance_diff = form.opening_balance.data - account.opening_balance
            account.opening_balance = form.opening_balance.data
            account.current_balance += balance_diff
        
        try:
            db.session.commit()
            flash(f'Account "{account.name}" has been updated successfully.', 'success')
            return redirect(url_for('accounts.show', account_id=account.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the account. Please try again.', 'error')
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.code.data = account.code
        form.name.data = account.name
        form.type.data = account.type.value
        form.parent_id.data = account.parent_id
        form.description.data = account.description
        form.opening_balance.data = account.opening_balance
        form.is_active.data = account.is_active
    
    return render_template('accounts/edit.html', form=form, account=account)

@accounts_bp.route('/<int:account_id>/delete', methods=['POST'])
def delete(account_id):
    """Delete an account"""
    account = Account.query.get_or_404(account_id)
    
    # Check if account has children
    children = Account.query.filter_by(parent_id=account_id).count()
    if children > 0:
        flash('Cannot delete account with child accounts. Please remove or reassign child accounts first.', 'error')
        return redirect(url_for('accounts.show', account_id=account_id))
    
    # Check if account has transactions (placeholder check)
    # TODO: Implement transaction checking when transaction models are created
    
    try:
        db.session.delete(account)
        db.session.commit()
        flash(f'Account "{account.name}" has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the account. Please try again.', 'error')
    
    return redirect(url_for('accounts.index'))

@accounts_bp.route('/api/hierarchy')
def api_hierarchy():
    """API endpoint to get account hierarchy as JSON"""
    accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
    
    def account_to_dict(account):
        return {
            'id': account.id,
            'code': account.code,
            'name': account.name,
            'type': account.type.value,
            'parent_id': account.parent_id,
            'current_balance': float(account.current_balance or 0),
            'children': []
        }
    
    # Build hierarchy
    account_dict = {account.id: account_to_dict(account) for account in accounts}
    root_accounts = []
    
    for account in accounts:
        account_data = account_dict[account.id]
        if account.parent_id and account.parent_id in account_dict:
            account_dict[account.parent_id]['children'].append(account_data)
        else:
            root_accounts.append(account_data)
    
    return jsonify(root_accounts)
