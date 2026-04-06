"""
Expense management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import desc, func, or_

from packages.server.src.models import (
    Expense, ExpenseLineItem, Vendor, Account, AccountType,
    PaymentMethod, ExpenseStatus, JournalEntry, JournalLineItem, TaxCode
)
from packages.server.src.database import db

expenses_bp = Blueprint('expenses_mgmt', __name__)


@expenses_bp.route('/')
@login_required
def index():
    """List all expenses"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    vendor_filter = request.args.get('vendor', '')
    search = request.args.get('search', '')

    query = Expense.query.filter(Expense.organization_id == current_user.organization_id)

    if status_filter:
        query = query.filter(Expense.status == status_filter)
    if vendor_filter:
        query = query.filter(Expense.vendor_id == vendor_filter)
    if search:
        query = query.filter(
            or_(
                Expense.expense_number.ilike(f'%{search}%'),
                Expense.description.ilike(f'%{search}%'),
                Expense.reference.ilike(f'%{search}%')
            )
        )

    query = query.order_by(desc(Expense.expense_date), desc(Expense.id))
    expenses = query.paginate(page=page, per_page=per_page, error_out=False)

    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.is_active == True
    ).order_by(Vendor.display_name).all()

    total_expenses = Expense.query.filter(
        Expense.organization_id == current_user.organization_id,
        Expense.status != ExpenseStatus.CANCELLED
    ).count()

    total_amount = db.session.query(func.sum(Expense.total)).filter(
        Expense.organization_id == current_user.organization_id,
        Expense.status != ExpenseStatus.CANCELLED
    ).scalar() or Decimal('0.00')

    stats = {
        'total_expenses': total_expenses,
        'total_amount': total_amount
    }

    return render_template('expenses/index.html',
                         expenses=expenses,
                         vendors=vendors,
                         stats=stats,
                         ExpenseStatus=ExpenseStatus,
                         today=date.today())


@expenses_bp.route('/create')
@login_required
def create():
    """Show expense creation form"""
    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.is_active == True
    ).order_by(Vendor.display_name).all()

    expense_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.EXPENSE,
        Account.is_active == True
    ).order_by(Account.name).all()

    payment_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        Account.is_active == True,
        or_(
            Account.name.ilike('%cash%'),
            Account.name.ilike('%bank%'),
            Account.name.ilike('%checking%')
        )
    ).order_by(Account.name).all()

    tax_codes = TaxCode.query.filter(
        TaxCode.organization_id == current_user.organization_id,
        TaxCode.is_active == True
    ).all()

    last_expense = Expense.query.filter(
        Expense.organization_id == current_user.organization_id
    ).order_by(desc(Expense.id)).first()

    if last_expense:
        try:
            last_num = int(last_expense.expense_number.split('-')[-1])
            next_number = f"EXP-{last_num + 1:04d}"
        except (ValueError, IndexError):
            next_number = f"EXP-{Expense.query.filter(Expense.organization_id == current_user.organization_id).count() + 1:04d}"
    else:
        next_number = "EXP-0001"

    return render_template('expenses/create.html',
                         vendors=vendors,
                         expense_accounts=expense_accounts,
                         payment_accounts=payment_accounts,
                         tax_codes=tax_codes,
                         next_number=next_number,
                         PaymentMethod=PaymentMethod,
                         today=date.today())


@expenses_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save expense"""
    try:
        expense_id = request.form.get('expense_id')
        expense_number = request.form.get('expense_number')
        expense_date = request.form.get('expense_date')
        vendor_id = request.form.get('vendor_id') or None
        payment_account_id = request.form.get('payment_account_id') or None
        payment_method = request.form.get('payment_method') or None
        reference = request.form.get('reference', '')
        description = request.form.get('description', '')
        notes = request.form.get('notes', '')

        if not all([expense_number, expense_date]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('expenses_mgmt.create'))

        expense_date = datetime.strptime(expense_date, '%Y-%m-%d').date()

        if expense_id:
            expense = Expense.query.get_or_404(expense_id)
            if expense.organization_id != current_user.organization_id:
                flash('Expense not found.', 'error')
                return redirect(url_for('expenses_mgmt.index'))
        else:
            expense = Expense(
                organization_id=current_user.organization_id,
                expense_number=expense_number,
                created_by=current_user.id
            )

        expense.expense_date = expense_date
        expense.vendor_id = vendor_id
        expense.payment_account_id = payment_account_id
        expense.payment_method = PaymentMethod(payment_method) if payment_method else None
        expense.reference = reference
        expense.description = description
        expense.notes = notes

        # Process line items
        line_descriptions = request.form.getlist('line_description[]')
        line_amounts = request.form.getlist('line_amount[]')
        line_account_ids = request.form.getlist('line_account_id[]')
        line_tax_code_ids = request.form.getlist('line_tax_code_id[]')

        if expense_id:
            ExpenseLineItem.query.filter(ExpenseLineItem.expense_id == expense.id).delete()

        subtotal = Decimal('0.00')
        total_tax = Decimal('0.00')
        line_items = []

        for i in range(len(line_descriptions)):
            if line_descriptions[i].strip() and line_amounts[i]:
                try:
                    amount = Decimal(line_amounts[i])
                    account_id = line_account_ids[i] if i < len(line_account_ids) and line_account_ids[i] else None
                    tax_code_id = line_tax_code_ids[i] if i < len(line_tax_code_ids) and line_tax_code_ids[i] else None

                    tax_amount = Decimal('0.00')
                    if tax_code_id:
                        tax_code = TaxCode.query.get(int(tax_code_id))
                        if tax_code:
                            tax_amount = amount * (tax_code.rate / Decimal('100'))

                    line_item = ExpenseLineItem(
                        account_id=account_id,
                        description=line_descriptions[i],
                        amount=amount,
                        tax_code_id=tax_code_id,
                        tax_amount=tax_amount,
                        tax_rate=tax_code.rate if tax_code_id and tax_code else Decimal('0')
                    )
                    line_items.append(line_item)
                    subtotal += amount
                    total_tax += tax_amount
                except (ValueError, TypeError):
                    continue

        if not line_items:
            flash('Please add at least one line item.', 'error')
            return redirect(url_for('expenses_mgmt.create'))

        expense.subtotal = subtotal
        expense.tax_amount = total_tax
        expense.total = subtotal + total_tax

        if not expense_id:
            db.session.add(expense)
            db.session.flush()

        for line_item in line_items:
            line_item.expense_id = expense.id
            db.session.add(line_item)

        db.session.commit()
        flash('Expense saved successfully!', 'success')
        return redirect(url_for('expenses_mgmt.view', id=expense.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error saving expense: {str(e)}', 'error')
        return redirect(url_for('expenses_mgmt.create'))


@expenses_bp.route('/view/<int:id>')
@login_required
def view(id):
    """View expense details"""
    expense = Expense.query.filter(
        Expense.id == id,
        Expense.organization_id == current_user.organization_id
    ).first_or_404()
    return render_template('expenses/view.html', expense=expense, ExpenseStatus=ExpenseStatus)


@expenses_bp.route('/edit/<int:id>')
@login_required
def edit(id):
    """Edit expense"""
    expense = Expense.query.filter(
        Expense.id == id,
        Expense.organization_id == current_user.organization_id
    ).first_or_404()

    if expense.status not in [ExpenseStatus.DRAFT, ExpenseStatus.PENDING]:
        flash('This expense cannot be edited.', 'error')
        return redirect(url_for('expenses_mgmt.view', id=id))

    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.is_active == True
    ).order_by(Vendor.display_name).all()

    expense_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.EXPENSE,
        Account.is_active == True
    ).order_by(Account.name).all()

    payment_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        Account.is_active == True,
        or_(Account.name.ilike('%cash%'), Account.name.ilike('%bank%'))
    ).order_by(Account.name).all()

    tax_codes = TaxCode.query.filter(
        TaxCode.organization_id == current_user.organization_id,
        TaxCode.is_active == True
    ).all()

    return render_template('expenses/edit.html',
                         expense=expense,
                         vendors=vendors,
                         expense_accounts=expense_accounts,
                         payment_accounts=payment_accounts,
                         tax_codes=tax_codes,
                         PaymentMethod=PaymentMethod)


@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete expense"""
    expense = Expense.query.filter(
        Expense.id == id,
        Expense.organization_id == current_user.organization_id
    ).first_or_404()

    if expense.status not in [ExpenseStatus.DRAFT, ExpenseStatus.PENDING]:
        flash('This expense cannot be deleted.', 'error')
        return redirect(url_for('expenses_mgmt.view', id=id))

    try:
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting expense: {str(e)}', 'error')

    return redirect(url_for('expenses_mgmt.index'))


@expenses_bp.route('/approve/<int:id>', methods=['POST'])
@login_required
def approve(id):
    """Approve and record expense"""
    expense = Expense.query.filter(
        Expense.id == id,
        Expense.organization_id == current_user.organization_id
    ).first_or_404()

    if expense.status not in [ExpenseStatus.DRAFT, ExpenseStatus.PENDING]:
        flash('This expense cannot be approved.', 'error')
        return redirect(url_for('expenses_mgmt.view', id=id))

    try:
        expense.status = ExpenseStatus.PAID

        # Create journal entry
        entry = JournalEntry(
            organization_id=current_user.organization_id,
            entry_number=f"EXP-{expense.expense_number}",
            date=expense.expense_date,
            description=f"Expense {expense.expense_number}" + (f" - {expense.vendor.display_name}" if expense.vendor else ""),
            source_type='expense',
            source_id=expense.id,
            created_by=current_user.id,
            debit_total=expense.total,
            credit_total=expense.total
        )
        db.session.add(entry)
        db.session.flush()

        # Debit expense accounts
        for line_item in expense.line_items:
            if line_item.account_id:
                db.session.add(JournalLineItem(
                    journal_entry_id=entry.id,
                    account_id=line_item.account_id,
                    description=line_item.description,
                    debit=line_item.amount + (line_item.tax_amount or Decimal('0')),
                    credit=Decimal('0.00'),
                    contact_type='vendor' if expense.vendor_id else None,
                    contact_id=expense.vendor_id
                ))

        # Credit payment account
        if expense.payment_account_id:
            db.session.add(JournalLineItem(
                journal_entry_id=entry.id,
                account_id=expense.payment_account_id,
                description=f"Expense {expense.expense_number}",
                debit=Decimal('0.00'),
                credit=expense.total
            ))

        db.session.commit()
        flash('Expense approved and recorded!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving expense: {str(e)}', 'error')

    return redirect(url_for('expenses_mgmt.view', id=id))
