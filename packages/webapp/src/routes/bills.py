"""
Bill (Purchase Bill) management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import desc, func, and_, or_

from packages.server.src.models import (
    Bill, BillLineItem, BillPayment, BillPaymentAllocation,
    Vendor, Item, Account, AccountType, BillStatus,
    PaymentMethod, JournalEntry, JournalLineItem, TaxCode
)
from packages.server.src.database import db

bills_bp = Blueprint('bills', __name__)


@bills_bp.route('/')
@login_required
def index():
    """List all bills with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    vendor_filter = request.args.get('vendor', '')
    search = request.args.get('search', '')

    query = Bill.query.filter(Bill.organization_id == current_user.organization_id)

    if status_filter:
        query = query.filter(Bill.status == status_filter)
    if vendor_filter:
        query = query.filter(Bill.vendor_id == vendor_filter)
    if search:
        query = query.join(Vendor).filter(
            or_(
                Bill.bill_number.ilike(f'%{search}%'),
                Bill.reference.ilike(f'%{search}%'),
                Vendor.display_name.ilike(f'%{search}%')
            )
        )

    query = query.order_by(desc(Bill.bill_date), desc(Bill.id))
    bills = query.paginate(page=page, per_page=per_page, error_out=False)

    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.is_active == True
    ).order_by(Vendor.display_name).all()

    total_bills = Bill.query.filter(
        Bill.organization_id == current_user.organization_id
    ).count()

    total_amount = db.session.query(func.sum(Bill.total)).filter(
        Bill.organization_id == current_user.organization_id,
        Bill.status != BillStatus.CANCELLED
    ).scalar() or Decimal('0.00')

    paid_amount = db.session.query(func.sum(Bill.paid_amount)).filter(
        Bill.organization_id == current_user.organization_id,
        Bill.status != BillStatus.CANCELLED
    ).scalar() or Decimal('0.00')

    outstanding_amount = db.session.query(func.sum(Bill.balance)).filter(
        Bill.organization_id == current_user.organization_id,
        Bill.balance > 0,
        Bill.status.in_([BillStatus.RECEIVED, BillStatus.PARTIAL, BillStatus.OVERDUE])
    ).scalar() or Decimal('0.00')

    stats = {
        'total_bills': total_bills,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'outstanding_amount': outstanding_amount
    }

    return render_template('bills/index.html',
                         bills=bills,
                         vendors=vendors,
                         stats=stats,
                         BillStatus=BillStatus,
                         today=date.today())


@bills_bp.route('/create')
@login_required
def create():
    """Show bill creation form"""
    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.is_active == True
    ).order_by(Vendor.display_name).all()

    items = Item.query.filter(
        Item.organization_id == current_user.organization_id,
        Item.is_active == True
    ).order_by(Item.name).all()

    expense_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.EXPENSE,
        Account.is_active == True
    ).order_by(Account.name).all()

    tax_codes = TaxCode.query.filter(
        TaxCode.organization_id == current_user.organization_id,
        TaxCode.is_active == True
    ).all()

    last_bill = Bill.query.filter(
        Bill.organization_id == current_user.organization_id
    ).order_by(desc(Bill.id)).first()

    if last_bill:
        try:
            last_num = int(last_bill.bill_number.split('-')[-1])
            next_number = f"BILL-{last_num + 1:04d}"
        except (ValueError, IndexError):
            next_number = f"BILL-{Bill.query.filter(Bill.organization_id == current_user.organization_id).count() + 1:04d}"
    else:
        next_number = "BILL-0001"

    return render_template('bills/create.html',
                         vendors=vendors,
                         items=items,
                         expense_accounts=expense_accounts,
                         tax_codes=tax_codes,
                         next_number=next_number,
                         today=date.today())


@bills_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save new or updated bill"""
    try:
        bill_id = request.form.get('bill_id')
        vendor_id = request.form.get('vendor_id')
        bill_number = request.form.get('bill_number')
        bill_date = request.form.get('bill_date')
        due_date = request.form.get('due_date')
        vendor_bill_number = request.form.get('vendor_bill_number', '')
        reference = request.form.get('reference', '')
        terms = request.form.get('terms', '')
        notes = request.form.get('notes', '')

        if not all([vendor_id, bill_number, bill_date, due_date]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('bills.create'))

        try:
            bill_date = datetime.strptime(bill_date, '%Y-%m-%d').date()
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'error')
            return redirect(url_for('bills.create'))

        if not bill_id:
            existing = Bill.query.filter(
                Bill.organization_id == current_user.organization_id,
                Bill.bill_number == bill_number
            ).first()
            if existing:
                flash('Bill number already exists.', 'error')
                return redirect(url_for('bills.create'))

        if bill_id:
            bill = Bill.query.get_or_404(bill_id)
            if bill.organization_id != current_user.organization_id:
                flash('Bill not found.', 'error')
                return redirect(url_for('bills.index'))
        else:
            bill = Bill(
                organization_id=current_user.organization_id,
                bill_number=bill_number
            )

        bill.vendor_id = vendor_id
        bill.bill_date = bill_date
        bill.due_date = due_date
        bill.vendor_bill_number = vendor_bill_number
        bill.reference = reference
        bill.terms = terms
        bill.notes = notes

        # Process line items
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        rates = request.form.getlist('rate[]')
        account_ids = request.form.getlist('account_id[]')
        item_ids = request.form.getlist('item_id[]')
        tax_code_ids = request.form.getlist('tax_code_id[]')

        if bill_id:
            BillLineItem.query.filter(BillLineItem.bill_id == bill.id).delete()

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
                    tax_code_id = tax_code_ids[i] if i < len(tax_code_ids) and tax_code_ids[i] else None
                    if tax_code_id:
                        tax_code = TaxCode.query.get(int(tax_code_id))
                        if tax_code:
                            tax_amount = amount * (tax_code.rate / Decimal('100'))

                    line_item = BillLineItem(
                        item_id=item_ids[i] if i < len(item_ids) and item_ids[i] else None,
                        description=descriptions[i],
                        quantity=quantity,
                        rate=rate,
                        amount=amount,
                        account_id=account_ids[i] if i < len(account_ids) and account_ids[i] else None,
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
            return redirect(url_for('bills.create'))

        total = subtotal + total_tax
        bill.subtotal = subtotal
        bill.tax_amount = total_tax
        bill.total = total
        bill.balance = total - (bill.paid_amount or Decimal('0.00'))

        if not bill_id:
            db.session.add(bill)
            db.session.flush()

        for line_item in line_items:
            line_item.bill_id = bill.id
            db.session.add(line_item)

        db.session.commit()
        flash('Bill saved successfully!', 'success')
        return redirect(url_for('bills.view', id=bill.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error saving bill: {str(e)}', 'error')
        return redirect(url_for('bills.create'))


@bills_bp.route('/view/<int:id>')
@login_required
def view(id):
    """View bill details"""
    bill = Bill.query.filter(
        Bill.id == id,
        Bill.organization_id == current_user.organization_id
    ).first_or_404()
    return render_template('bills/view.html', bill=bill, BillStatus=BillStatus)


@bills_bp.route('/edit/<int:id>')
@login_required
def edit(id):
    """Edit bill"""
    bill = Bill.query.filter(
        Bill.id == id,
        Bill.organization_id == current_user.organization_id
    ).first_or_404()

    if bill.status != BillStatus.DRAFT:
        flash('Only draft bills can be edited.', 'error')
        return redirect(url_for('bills.view', id=id))

    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.is_active == True
    ).order_by(Vendor.display_name).all()

    items = Item.query.filter(
        Item.organization_id == current_user.organization_id,
        Item.is_active == True
    ).order_by(Item.name).all()

    expense_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.EXPENSE,
        Account.is_active == True
    ).order_by(Account.name).all()

    tax_codes = TaxCode.query.filter(
        TaxCode.organization_id == current_user.organization_id,
        TaxCode.is_active == True
    ).all()

    return render_template('bills/edit.html',
                         bill=bill,
                         vendors=vendors,
                         items=items,
                         expense_accounts=expense_accounts,
                         tax_codes=tax_codes)


@bills_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete bill"""
    bill = Bill.query.filter(
        Bill.id == id,
        Bill.organization_id == current_user.organization_id
    ).first_or_404()

    if bill.status != BillStatus.DRAFT:
        flash('Only draft bills can be deleted.', 'error')
        return redirect(url_for('bills.view', id=id))

    try:
        db.session.delete(bill)
        db.session.commit()
        flash('Bill deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting bill: {str(e)}', 'error')

    return redirect(url_for('bills.index'))


@bills_bp.route('/approve/<int:id>', methods=['POST'])
@login_required
def approve(id):
    """Approve/receive a bill (moves from draft to received)"""
    bill = Bill.query.filter(
        Bill.id == id,
        Bill.organization_id == current_user.organization_id
    ).first_or_404()

    if bill.status != BillStatus.DRAFT:
        flash('Only draft bills can be approved.', 'error')
        return redirect(url_for('bills.view', id=id))

    try:
        bill.status = BillStatus.RECEIVED
        create_bill_journal_entry(bill)
        db.session.commit()
        flash('Bill approved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving bill: {str(e)}', 'error')

    return redirect(url_for('bills.view', id=id))


def create_bill_journal_entry(bill):
    """Create accounting journal entry for a bill"""
    accounts_payable = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.LIABILITY,
        Account.name.ilike('%payable%')
    ).first()

    if not accounts_payable:
        raise Exception("Accounts Payable account not found. Please set it up first.")

    entry = JournalEntry(
        organization_id=current_user.organization_id,
        entry_number=f"BILL-{bill.bill_number}",
        date=bill.bill_date,
        description=f"Bill {bill.bill_number} - {bill.vendor.display_name}",
        source_type='bill',
        source_id=bill.id,
        created_by=current_user.id,
        debit_total=bill.total,
        credit_total=bill.total
    )
    db.session.add(entry)
    db.session.flush()

    # Debit expense accounts (from line items)
    for line_item in bill.line_items:
        expense_account = line_item.account
        if not expense_account:
            expense_account = Account.query.filter(
                Account.organization_id == current_user.organization_id,
                Account.type == AccountType.EXPENSE
            ).first()
        if expense_account:
            debit_line = JournalLineItem(
                journal_entry_id=entry.id,
                account_id=expense_account.id,
                description=line_item.description,
                debit=line_item.amount + (line_item.tax_amount or Decimal('0')),
                credit=Decimal('0.00'),
                contact_type='vendor',
                contact_id=bill.vendor_id
            )
            db.session.add(debit_line)

    # Credit Accounts Payable
    credit_line = JournalLineItem(
        journal_entry_id=entry.id,
        account_id=accounts_payable.id,
        description=f"Bill {bill.bill_number}",
        debit=Decimal('0.00'),
        credit=bill.total,
        contact_type='vendor',
        contact_id=bill.vendor_id
    )
    db.session.add(credit_line)


@bills_bp.route('/pay/<int:id>')
@login_required
def pay(id):
    """Show bill payment form"""
    bill = Bill.query.filter(
        Bill.id == id,
        Bill.organization_id == current_user.organization_id
    ).first_or_404()

    if bill.status not in [BillStatus.RECEIVED, BillStatus.PARTIAL, BillStatus.OVERDUE]:
        flash('This bill cannot be paid.', 'error')
        return redirect(url_for('bills.view', id=id))

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

    last_payment = BillPayment.query.filter(
        BillPayment.organization_id == current_user.organization_id
    ).order_by(desc(BillPayment.id)).first()

    if last_payment:
        try:
            last_num = int(last_payment.payment_number.split('-')[-1])
            next_number = f"BP-{last_num + 1:04d}"
        except (ValueError, IndexError):
            next_number = f"BP-{BillPayment.query.filter(BillPayment.organization_id == current_user.organization_id).count() + 1:04d}"
    else:
        next_number = "BP-0001"

    return render_template('bills/pay.html',
                         bill=bill,
                         payment_accounts=payment_accounts,
                         next_number=next_number,
                         PaymentMethod=PaymentMethod,
                         today=date.today())


@bills_bp.route('/record-payment/<int:id>', methods=['POST'])
@login_required
def record_payment(id):
    """Record a payment against a bill"""
    bill = Bill.query.filter(
        Bill.id == id,
        Bill.organization_id == current_user.organization_id
    ).first_or_404()

    try:
        payment_amount = Decimal(request.form.get('amount', '0'))
        payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date()
        payment_method = request.form.get('payment_method')
        payment_account_id = request.form.get('payment_account_id')
        payment_number = request.form.get('payment_number')
        reference = request.form.get('reference', '')
        notes = request.form.get('notes', '')

        if payment_amount <= 0 or payment_amount > bill.balance:
            flash('Invalid payment amount.', 'error')
            return redirect(url_for('bills.pay', id=id))

        payment = BillPayment(
            payment_number=payment_number,
            payment_date=payment_date,
            amount=payment_amount,
            payment_method=PaymentMethod(payment_method),
            vendor_id=bill.vendor_id,
            payment_account_id=payment_account_id,
            organization_id=current_user.organization_id,
            created_by=current_user.id,
            reference=reference,
            notes=notes
        )
        db.session.add(payment)
        db.session.flush()

        allocation = BillPaymentAllocation(
            bill_payment_id=payment.id,
            bill_id=bill.id,
            allocated_amount=payment_amount
        )
        db.session.add(allocation)

        bill.paid_amount = (bill.paid_amount or Decimal('0')) + payment_amount
        bill.balance = bill.total - bill.paid_amount

        if bill.balance <= 0:
            bill.status = BillStatus.PAID
        else:
            bill.status = BillStatus.PARTIAL

        # Create journal entry for payment
        accounts_payable = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.LIABILITY,
            Account.name.ilike('%payable%')
        ).first()

        if accounts_payable:
            entry = JournalEntry(
                organization_id=current_user.organization_id,
                entry_number=f"BP-{payment.payment_number}",
                date=payment_date,
                description=f"Payment for Bill {bill.bill_number}",
                source_type='bill_payment',
                source_id=payment.id,
                created_by=current_user.id,
                debit_total=payment_amount,
                credit_total=payment_amount
            )
            db.session.add(entry)
            db.session.flush()

            # Debit Accounts Payable
            db.session.add(JournalLineItem(
                journal_entry_id=entry.id,
                account_id=accounts_payable.id,
                description=f"Payment - Bill {bill.bill_number}",
                debit=payment_amount,
                credit=Decimal('0.00'),
                contact_type='vendor',
                contact_id=bill.vendor_id
            ))
            # Credit Bank/Cash
            db.session.add(JournalLineItem(
                journal_entry_id=entry.id,
                account_id=int(payment_account_id),
                description=f"Payment - Bill {bill.bill_number}",
                debit=Decimal('0.00'),
                credit=payment_amount
            ))

        db.session.commit()
        flash('Payment recorded successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error recording payment: {str(e)}', 'error')

    return redirect(url_for('bills.view', id=id))


@bills_bp.route('/api/items/<int:item_id>')
@login_required
def get_item_details(item_id):
    """Get item details for bill line items (AJAX)"""
    item = Item.query.filter(
        Item.id == item_id,
        Item.organization_id == current_user.organization_id
    ).first()

    if not item:
        return jsonify({'error': 'Item not found'}), 404

    return jsonify({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'cost_price': str(item.cost_price),
        'unit': item.unit
    })
