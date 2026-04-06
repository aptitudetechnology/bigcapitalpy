"""
Sale Receipt management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import desc, func

from packages.server.src.models import (
    SaleReceipt, SaleReceiptLineItem, Customer, Item, Account, AccountType,
    SaleReceiptStatus, JournalEntry, JournalLineItem, TaxCode, PaymentMethod
)
from packages.server.src.database import db

sale_receipts_bp = Blueprint('sale_receipts', __name__)


@sale_receipts_bp.route('/')
@login_required
def index():
    """List all sale receipts"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')

    query = SaleReceipt.query.filter(SaleReceipt.organization_id == current_user.organization_id)

    if status_filter:
        query = query.filter(SaleReceipt.status == status_filter)

    if search:
        query = query.join(Customer).filter(
            db.or_(
                SaleReceipt.receipt_number.ilike(f'%{search}%'),
                Customer.display_name.ilike(f'%{search}%')
            )
        )

    query = query.order_by(desc(SaleReceipt.receipt_date), desc(SaleReceipt.id))
    receipts = query.paginate(page=page, per_page=per_page, error_out=False)

    # Summary statistics
    total_receipts = SaleReceipt.query.filter(
        SaleReceipt.organization_id == current_user.organization_id
    ).count()

    total_amount = db.session.query(func.sum(SaleReceipt.total)).filter(
        SaleReceipt.organization_id == current_user.organization_id,
        SaleReceipt.status != SaleReceiptStatus.CANCELLED
    ).scalar() or Decimal('0.00')

    closed_amount = db.session.query(func.sum(SaleReceipt.total)).filter(
        SaleReceipt.organization_id == current_user.organization_id,
        SaleReceipt.status == SaleReceiptStatus.CLOSED
    ).scalar() or Decimal('0.00')

    draft_count = SaleReceipt.query.filter(
        SaleReceipt.organization_id == current_user.organization_id,
        SaleReceipt.status == SaleReceiptStatus.DRAFT
    ).count()

    stats = {
        'total_receipts': total_receipts,
        'total_amount': total_amount,
        'closed_amount': closed_amount,
        'draft_count': draft_count
    }

    return render_template('sale_receipts/index.html',
                         receipts=receipts,
                         stats=stats,
                         SaleReceiptStatus=SaleReceiptStatus,
                         today=date.today())


@sale_receipts_bp.route('/create')
@login_required
def create():
    """Show sale receipt creation form"""
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()

    items = Item.query.filter(
        Item.organization_id == current_user.organization_id,
        Item.is_active == True
    ).order_by(Item.name).all()

    # Generate next receipt number
    last = SaleReceipt.query.filter(
        SaleReceipt.organization_id == current_user.organization_id
    ).order_by(desc(SaleReceipt.id)).first()

    if last:
        try:
            last_num = int(last.receipt_number.split('-')[-1])
            next_number = f"SR-{last_num + 1:04d}"
        except (ValueError, IndexError):
            next_number = f"SR-{SaleReceipt.query.filter(SaleReceipt.organization_id == current_user.organization_id).count() + 1:04d}"
    else:
        next_number = "SR-0001"

    # Deposit accounts (bank/cash)
    deposit_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        db.or_(
            Account.name.ilike('%bank%'),
            Account.name.ilike('%cash%'),
            Account.name.ilike('%checking%')
        )
    ).all()

    tax_codes = TaxCode.query.filter(
        TaxCode.organization_id == current_user.organization_id,
        TaxCode.is_active == True
    ).all()

    return render_template('sale_receipts/create.html',
                         customers=customers,
                         items=items,
                         next_number=next_number,
                         deposit_accounts=deposit_accounts,
                         tax_codes=tax_codes,
                         PaymentMethod=PaymentMethod,
                         today=date.today())


@sale_receipts_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save new or updated sale receipt"""
    try:
        receipt_id = request.form.get('receipt_id')

        customer_id = request.form.get('customer_id')
        receipt_number = request.form.get('receipt_number')
        receipt_date = request.form.get('receipt_date')
        deposit_account_id = request.form.get('deposit_account_id')
        payment_method = request.form.get('payment_method')
        reference = request.form.get('reference', '')
        statement_message = request.form.get('statement_message', '')
        notes = request.form.get('notes', '')

        if not all([customer_id, receipt_number, receipt_date]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('sale_receipts.create'))

        try:
            receipt_date = datetime.strptime(receipt_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'error')
            return redirect(url_for('sale_receipts.create'))

        if not receipt_id:
            existing = SaleReceipt.query.filter(
                SaleReceipt.organization_id == current_user.organization_id,
                SaleReceipt.receipt_number == receipt_number
            ).first()
            if existing:
                flash('Receipt number already exists.', 'error')
                return redirect(url_for('sale_receipts.create'))

        if receipt_id:
            receipt = SaleReceipt.query.get_or_404(receipt_id)
            if receipt.organization_id != current_user.organization_id:
                flash('Receipt not found.', 'error')
                return redirect(url_for('sale_receipts.index'))
        else:
            receipt = SaleReceipt(
                organization_id=current_user.organization_id,
                receipt_number=receipt_number,
                created_by=current_user.id
            )

        receipt.customer_id = customer_id
        receipt.receipt_date = receipt_date
        receipt.deposit_account_id = deposit_account_id or None
        receipt.payment_method = PaymentMethod(payment_method) if payment_method else None
        receipt.reference = reference
        receipt.statement_message = statement_message
        receipt.notes = notes

        # Process line items
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        rates = request.form.getlist('rate[]')
        item_ids = request.form.getlist('item_id[]')
        tax_code_ids = request.form.getlist('tax_code_id[]')

        if receipt_id:
            SaleReceiptLineItem.query.filter(SaleReceiptLineItem.sale_receipt_id == receipt.id).delete()

        subtotal = Decimal('0.00')
        total_tax = Decimal('0.00')
        line_items = []

        for i in range(len(descriptions)):
            if descriptions[i].strip():
                try:
                    quantity = Decimal(quantities[i] or '0')
                    rate = Decimal(rates[i] or '0')
                    amount = quantity * rate

                    tax_amount = Decimal('0.00')
                    tax_rate = Decimal('0')
                    tax_code_id = tax_code_ids[i] if i < len(tax_code_ids) and tax_code_ids[i] else None
                    if tax_code_id:
                        tax_code = TaxCode.query.get(int(tax_code_id))
                        if tax_code:
                            tax_rate = tax_code.rate
                            tax_amount = amount * (tax_rate / Decimal('100'))

                    line_item = SaleReceiptLineItem(
                        item_id=item_ids[i] if i < len(item_ids) and item_ids[i] else None,
                        description=descriptions[i],
                        quantity=quantity,
                        rate=rate,
                        amount=amount,
                        tax_code_id=tax_code_id,
                        tax_rate=tax_rate,
                        tax_amount=tax_amount
                    )
                    line_items.append(line_item)
                    subtotal += amount
                    total_tax += tax_amount
                except (ValueError, TypeError):
                    continue

        if not line_items:
            flash('Please add at least one line item.', 'error')
            return redirect(url_for('sale_receipts.create'))

        receipt.subtotal = subtotal
        receipt.tax_amount = total_tax
        receipt.total = subtotal + total_tax

        if not receipt_id:
            db.session.add(receipt)
            db.session.flush()

        for line_item in line_items:
            line_item.sale_receipt_id = receipt.id
            db.session.add(line_item)

        db.session.commit()

        flash('Sale receipt saved successfully!', 'success')
        return redirect(url_for('sale_receipts.view', id=receipt.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error saving sale receipt: {str(e)}', 'error')
        return redirect(url_for('sale_receipts.create'))


@sale_receipts_bp.route('/view/<int:id>')
@login_required
def view(id):
    """View sale receipt details"""
    receipt = SaleReceipt.query.filter(
        SaleReceipt.id == id,
        SaleReceipt.organization_id == current_user.organization_id
    ).first_or_404()

    return render_template('sale_receipts/view.html',
                         receipt=receipt,
                         SaleReceiptStatus=SaleReceiptStatus)


@sale_receipts_bp.route('/close/<int:id>', methods=['POST'])
@login_required
def close(id):
    """Close a sale receipt (marks payment received and creates journal entry)"""
    receipt = SaleReceipt.query.filter(
        SaleReceipt.id == id,
        SaleReceipt.organization_id == current_user.organization_id
    ).first_or_404()

    if receipt.status != SaleReceiptStatus.DRAFT:
        flash('Only draft receipts can be closed.', 'error')
        return redirect(url_for('sale_receipts.view', id=id))

    try:
        receipt.status = SaleReceiptStatus.CLOSED
        create_sale_receipt_journal_entry(receipt)
        db.session.commit()
        flash('Sale receipt closed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error closing sale receipt: {str(e)}', 'error')

    return redirect(url_for('sale_receipts.view', id=id))


@sale_receipts_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a draft sale receipt"""
    receipt = SaleReceipt.query.filter(
        SaleReceipt.id == id,
        SaleReceipt.organization_id == current_user.organization_id
    ).first_or_404()

    if receipt.status != SaleReceiptStatus.DRAFT:
        flash('Only draft receipts can be deleted.', 'error')
        return redirect(url_for('sale_receipts.view', id=id))

    try:
        db.session.delete(receipt)
        db.session.commit()
        flash('Sale receipt deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting sale receipt: {str(e)}', 'error')

    return redirect(url_for('sale_receipts.index'))


def create_sale_receipt_journal_entry(receipt):
    """Create journal entry for a closed sale receipt.
    Debit: Bank/Cash (deposit account)
    Credit: Sales Income
    """
    deposit_account = receipt.deposit_account
    if not deposit_account:
        deposit_account = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.ASSET,
            Account.name.ilike('%cash%')
        ).first()

    sales_account = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.INCOME,
        Account.name.ilike('%sales%')
    ).first()

    if not deposit_account or not sales_account:
        raise Exception("Required accounts not found. Please set up deposit and sales accounts.")

    entry = JournalEntry(
        organization_id=current_user.organization_id,
        entry_number=f"SR-{receipt.receipt_number}",
        date=receipt.receipt_date,
        description=f"Sale Receipt {receipt.receipt_number} - {receipt.customer.display_name}",
        source_type='sale_receipt',
        source_id=receipt.id,
        created_by=current_user.id,
        debit_total=receipt.total,
        credit_total=receipt.total
    )
    db.session.add(entry)
    db.session.flush()

    # Debit deposit account (Bank/Cash)
    debit_line = JournalLineItem(
        journal_entry_id=entry.id,
        account_id=deposit_account.id,
        description=f"Sale Receipt {receipt.receipt_number}",
        debit=receipt.total,
        credit=Decimal('0.00'),
        contact_type='customer',
        contact_id=receipt.customer_id
    )
    db.session.add(debit_line)

    # Credit Sales Income
    credit_line = JournalLineItem(
        journal_entry_id=entry.id,
        account_id=sales_account.id,
        description=f"Sales - Receipt {receipt.receipt_number}",
        debit=Decimal('0.00'),
        credit=receipt.total
    )
    db.session.add(credit_line)
