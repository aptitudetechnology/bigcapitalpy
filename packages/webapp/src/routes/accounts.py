"""
Accounts blueprint for BigCapitalPy.
Handles Chart of Accounts and related operations.

Balances shown here are derived from journal line items rather than from the
denormalised ``Account.current_balance`` column. That column is only written by
the manual-journal and bank-reconciliation flows in ``routes/financial.py``;
invoices, bills, payments and expenses post journal entries without touching it,
so it under-reports. The aggregation below mirrors the one used by
``routes/reports/financial.py:trial_balance`` so the two views agree.
"""

from decimal import Decimal

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import StringField, SelectField, TextAreaField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Length, Optional

from packages.server.src.database import db
from packages.server.src.models import Account, AccountType, JournalLineItem

accounts_bp = Blueprint('accounts', __name__)

# Account.type is an AccountType enum with five root values, so the picker offers
# exactly those. The 19 fine-grained types in accounts_constants.ACCOUNT_TYPES
# (bank, accounts-receivable, ...) have no column to live in yet; adding an
# account subtype is follow-up work.
ACCOUNT_TYPE_CHOICES = [
    (AccountType.ASSET.value, 'Asset'),
    (AccountType.LIABILITY.value, 'Liability'),
    (AccountType.EQUITY.value, 'Equity'),
    (AccountType.INCOME.value, 'Income'),
    (AccountType.EXPENSE.value, 'Expense'),
]

# Accounts whose natural (positive) balance is a debit balance. The rest are
# credit-normal, so their net is negated to read positive when normal.
DEBIT_NORMAL_TYPES = {AccountType.ASSET, AccountType.EXPENSE}

# Groups the summary tiles on the index page.
SUMMARY_GROUPS = [
    ('assets', AccountType.ASSET),
    ('liabilities', AccountType.LIABILITY),
    ('equity', AccountType.EQUITY),
    ('income', AccountType.INCOME),
    ('expense', AccountType.EXPENSE),
]


class AccountForm(FlaskForm):
    """Form for creating and editing accounts."""
    code = StringField('Account Code', validators=[DataRequired(), Length(min=1, max=20)])
    name = StringField('Account Name', validators=[DataRequired(), Length(min=1, max=255)])
    type = SelectField('Account Type', choices=ACCOUNT_TYPE_CHOICES, validators=[DataRequired()])
    parent_id = SelectField('Parent Account', choices=[], validators=[Optional()], coerce=int)
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    opening_balance = DecimalField('Opening Balance', places=2, validators=[Optional()])
    is_active = BooleanField('Active', default=True)


class _Summary:
    """Count/balance pair for one account-type tile on the index page."""

    def __init__(self, count=0, balance=Decimal('0.00')):
        self.count = count
        self.balance = balance


def _journal_balances(organization_id):
    """Map account_id -> net (debits - credits) for one organization.

    Single grouped query so the index page does not issue one query per account.
    """
    rows = (
        db.session.query(
            JournalLineItem.account_id,
            func.coalesce(func.sum(JournalLineItem.debit), 0).label('debits'),
            func.coalesce(func.sum(JournalLineItem.credit), 0).label('credits'),
        )
        .join(Account, Account.id == JournalLineItem.account_id)
        .filter(Account.organization_id == organization_id)
        .group_by(JournalLineItem.account_id)
        .all()
    )
    return {
        r.account_id: Decimal(str(r.debits)) - Decimal(str(r.credits))
        for r in rows
    }


def _natural_balance(account, net):
    """Sign a raw net so an account in its normal direction reads positive."""
    if account.type in DEBIT_NORMAL_TYPES:
        return net
    return -net


def _attach_balances(accounts, organization_id):
    """Set a transient ``.balance`` on each account for template rendering.

    The attribute is not a mapped column, so it is never persisted.
    """
    nets = _journal_balances(organization_id)
    for account in accounts:
        net = nets.get(account.id, Decimal('0.00'))
        account.balance = _natural_balance(account, net)
    return accounts


def _parent_choices(organization_id, exclude_id=None):
    """Parent-account choices, optionally excluding one account (and its subtree)."""
    query = Account.query.filter(Account.organization_id == organization_id)
    if exclude_id is not None:
        query = query.filter(Account.id != exclude_id)
    accounts = query.order_by(Account.code).all()

    if exclude_id is not None:
        # Prevent creating a cycle by re-parenting an account beneath its own
        # descendant.
        descendants = _descendant_ids(exclude_id, organization_id)
        accounts = [a for a in accounts if a.id not in descendants]

    return [(0, '-- None --')] + [
        (a.id, f'{a.code} - {a.name}') for a in accounts
    ]


def _descendant_ids(account_id, organization_id):
    """Collect all descendant account ids of ``account_id``."""
    children_map = {}
    for acc_id, parent_id in db.session.query(Account.id, Account.parent_id).filter(
        Account.organization_id == organization_id
    ):
        children_map.setdefault(parent_id, []).append(acc_id)

    found, stack = set(), list(children_map.get(account_id, []))
    while stack:
        current = stack.pop()
        if current in found:
            continue
        found.add(current)
        stack.extend(children_map.get(current, []))
    return found


def _code_taken(code, organization_id, exclude_id=None):
    query = Account.query.filter(
        Account.organization_id == organization_id,
        Account.code == code,
    )
    if exclude_id is not None:
        query = query.filter(Account.id != exclude_id)
    return db.session.query(query.exists()).scalar()


@accounts_bp.route('/')
@login_required
def index():
    """Chart of Accounts listing page."""
    org_id = current_user.organization_id

    query = Account.query.filter(Account.organization_id == org_id)

    search = (request.args.get('search') or '').strip()
    if search:
        term = f'%{search}%'
        query = query.filter(db.or_(Account.name.ilike(term), Account.code.ilike(term)))

    type_filter = (request.args.get('type') or '').strip()
    if type_filter:
        try:
            query = query.filter(Account.type == AccountType(type_filter))
        except ValueError:
            flash(f'Unknown account type filter: {type_filter}', 'warning')

    status_filter = (request.args.get('status') or '').strip()
    if status_filter == 'active':
        query = query.filter(Account.is_active.is_(True))
    elif status_filter == 'inactive':
        query = query.filter(Account.is_active.is_(False))

    accounts = _attach_balances(query.order_by(Account.code).all(), org_id)

    account_summary = type('AccountSummary', (), {})()
    for attr, account_type in SUMMARY_GROUPS:
        matching = [a for a in accounts if a.type == account_type]
        setattr(account_summary, attr, _Summary(
            count=len(matching),
            balance=sum((a.balance for a in matching), Decimal('0.00')),
        ))

    accounts_by_type = {}
    for account in accounts:
        accounts_by_type.setdefault(account.type.value, []).append(account)

    return render_template(
        'accounts/index.html',
        accounts=accounts,
        account_summary=account_summary,
        accounts_by_type=accounts_by_type,
    )


@accounts_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create a new account."""
    org_id = current_user.organization_id
    form = AccountForm()
    form.parent_id.choices = _parent_choices(org_id)

    if form.validate_on_submit():
        code = form.code.data.strip()
        if _code_taken(code, org_id):
            flash(f'Account code {code} is already in use.', 'error')
            return render_template('accounts/new.html', form=form)

        account = Account(
            code=code,
            name=form.name.data.strip(),
            type=AccountType(form.type.data),
            parent_id=form.parent_id.data or None,
            description=form.description.data,
            opening_balance=form.opening_balance.data or Decimal('0.00'),
            current_balance=form.opening_balance.data or Decimal('0.00'),
            is_active=form.is_active.data,
            organization_id=org_id,
        )
        db.session.add(account)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Error creating account.', 'error')
            return render_template('accounts/new.html', form=form)

        flash(f'Account {account.code} - {account.name} created successfully.', 'success')
        return redirect(url_for('accounts.show', account_id=account.id))

    return render_template('accounts/new.html', form=form)


@accounts_bp.route('/<int:account_id>')
@login_required
def show(account_id):
    """Show account details."""
    org_id = current_user.organization_id
    account = Account.query.filter(
        Account.id == account_id,
        Account.organization_id == org_id,
    ).first()

    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('accounts.index'))

    children = Account.query.filter(
        Account.parent_id == account.id,
        Account.organization_id == org_id,
    ).order_by(Account.code).all()

    _attach_balances([account] + children, org_id)

    return render_template('accounts/show.html', account=account, children=children)


@accounts_bp.route('/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(account_id):
    """Edit an existing account."""
    org_id = current_user.organization_id
    account = Account.query.filter(
        Account.id == account_id,
        Account.organization_id == org_id,
    ).first()

    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('accounts.index'))

    form = AccountForm(obj=account)
    form.parent_id.choices = _parent_choices(org_id, exclude_id=account.id)

    if request.method == 'GET':
        form.type.data = account.type.value
        form.parent_id.data = account.parent_id or 0

    if form.validate_on_submit():
        code = form.code.data.strip()
        if _code_taken(code, org_id, exclude_id=account.id):
            flash(f'Account code {code} is already in use.', 'error')
            return render_template('accounts/edit.html', form=form, account=account)

        account.code = code
        account.name = form.name.data.strip()
        account.type = AccountType(form.type.data)
        account.parent_id = form.parent_id.data or None
        account.description = form.description.data
        account.opening_balance = form.opening_balance.data or Decimal('0.00')
        account.is_active = form.is_active.data

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Error updating account.', 'error')
            return render_template('accounts/edit.html', form=form, account=account)

        flash(f'Account {account.code} - {account.name} updated successfully.', 'success')
        return redirect(url_for('accounts.show', account_id=account.id))

    return render_template('accounts/edit.html', form=form, account=account)


@accounts_bp.route('/<int:account_id>/delete', methods=['POST'])
@login_required
def delete(account_id):
    """Delete an account, provided nothing depends on it."""
    org_id = current_user.organization_id
    account = Account.query.filter(
        Account.id == account_id,
        Account.organization_id == org_id,
    ).first()

    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('accounts.index'))

    child_count = Account.query.filter(
        Account.parent_id == account.id,
        Account.organization_id == org_id,
    ).count()
    if child_count:
        flash(
            f'Cannot delete {account.code} - {account.name}: it has {child_count} '
            f'child account(s). Reassign or delete them first.',
            'error',
        )
        return redirect(url_for('accounts.show', account_id=account.id))

    entry_count = JournalLineItem.query.filter(
        JournalLineItem.account_id == account.id
    ).count()
    if entry_count:
        flash(
            f'Cannot delete {account.code} - {account.name}: it is used by '
            f'{entry_count} journal line(s). Deactivate it instead to keep the '
            f'audit trail intact.',
            'error',
        )
        return redirect(url_for('accounts.show', account_id=account.id))

    label = f'{account.code} - {account.name}'
    db.session.delete(account)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('Error deleting account.', 'error')
        return redirect(url_for('accounts.show', account_id=account.id))

    flash(f'Account {label} deleted.', 'success')
    return redirect(url_for('accounts.index'))
