"""
Vendor Credit management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import desc, func

from packages.server.src.models import (
    VendorCredit, VendorCreditLineItem, VendorCreditApplication,
    Vendor, Item, Bill, BillStatus, Account, AccountType,
    VendorCreditStatus, JournalEntry, JournalLineItem, TaxCode
)
from packages.server.src.database import db

vendor_credits_bp = Blueprint('vendor_credits', __name__)


@vendor_credits_bp.route('/')
@login_required
def index():
    """List all vendor credits"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = VendorCredit.query.filter(VendorCredit.organization_id == current_user.organization_id)
    query = query.order_by(desc(VendorCredit.credit_date), desc(VendorCredit.id))
    vendor_credits = query.paginate(page=page, per_page=per_page, error_out=False)

    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.is_active == True
    ).order_by(Vendor.display_name).all()

    total_amount = db.session.query(func.sum(VendorCredit.total)).filter(
        VendorCredit.organization_id == current_user.organization_id,
        VendorCredit.status != VendorCreditStatus.CANCELLED
    ).scalar() or Decimal('0.00')

    open_amount = db.session.query(func.sum(VendorCredit.balance)).filter(
        VendorCredit.organization_id == current_user.organization_id,
        VendorCredit.status.in_([VendorCreditStatus.OPEN, VendorCreditStatus.PARTIAL])
    ).scalar() or Decimal('0.00')

    stats = {
        'total_count': VendorCredit.query.filter(VendorCredit.organization_id == current_user.organization_id).count(),
        'total_amount': total_amount,
        'open_amount': open_amount
    }

    return render_template('vendor_credits/index.html',
                         vendor_credits=vendor_credits,
                         vendors=vendors,
                         stats=stats,
                         VendorCreditStatus=VendorCreditStatus)


@vendor_credits_bp.route('/create')
@login_required
def create():
    """Show vendor credit creation form"""
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

    last_vc = VendorCredit.query.filter(
        VendorCredit.organization_id == current_user.organization_id
    ).order_by(desc(VendorCredit.id)).first()

    if last_vc:
        try:
            last_num = int(last_vc.credit_number.split('-')[-1])
            next_number = f"VC-{last_num + 1:04d}"
        except (ValueError, IndexError):
            next_number = f"VC-{VendorCredit.query.filter(VendorCredit.organization_id == current_user.organization_id).count() + 1:04d}"
    else:
        next_number = "VC-0001"

    return render_template('vendor_credits/create.html',
                         vendors=vendors,
                         items=items,
                         expense_accounts=expense_accounts,
                         tax_codes=tax_codes,
                         next_number=next_number,
                         today=date.today())


@vendor_credits_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save vendor credit"""
    try:
        vc_id = request.form.get('vendor_credit_id')
        vendor_id = request.form.get('vendor_id')
        credit_number = request.form.get('credit_number')
        credit_date = request.form.get('credit_date')
        bill_id = request.form.get('bill_id') or None
        reference = request.form.get('reference', '')
        notes = request.form.get('notes', '')

        if not all([vendor_id, credit_number, credit_date]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('vendor_credits.create'))

        credit_date = datetime.strptime(credit_date, '%Y-%m-%d').date()

        if vc_id:
            vc = VendorCredit.query.get_or_404(vc_id)
            if vc.organization_id != current_user.organization_id:
                flash('Vendor credit not found.', 'error')
                return redirect(url_for('vendor_credits.index'))
        else:
            vc = VendorCredit(
                organization_id=current_user.organization_id,
                credit_number=credit_number
            )

        vc.vendor_id = vendor_id
        vc.credit_date = credit_date
        vc.bill_id = bill_id
        vc.reference = reference
        vc.notes = notes

        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        rates = request.form.getlist('rate[]')
        item_ids = request.form.getlist('item_id[]')
        account_ids = request.form.getlist('account_id[]')
        tax_code_ids = request.form.getlist('tax_code_id[]')

        if vc_id:
            VendorCreditLineItem.query.filter(VendorCreditLineItem.vendor_credit_id == vc.id).delete()

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
                        tc = TaxCode.query.get(int(tax_code_id))
                        if tc:
                            tax_amount = amount * (tc.rate / Decimal('100'))

                    line_item = VendorCreditLineItem(
                        item_id=item_ids[i] if i < len(item_ids) and item_ids[i] else None,
                        description=descriptions[i],
                        quantity=quantity,
                        rate=rate,
                        amount=amount,
                        account_id=account_ids[i] if i < len(account_ids) and account_ids[i] else None,
                        tax_code_id=tax_code_id,
                        tax_amount=tax_amount,
                        tax_rate=tc.rate if tax_code_id and tc else Decimal('0')
                    )
                    line_items.append(line_item)
                    subtotal += amount
                    total_tax += tax_amount
                except (ValueError, TypeError):
                    continue

        if not line_items:
            flash('Please add at least one line item.', 'error')
            return redirect(url_for('vendor_credits.create'))

        vc.subtotal = subtotal
        vc.tax_amount = total_tax
        vc.total = subtotal + total_tax
        vc.balance = vc.total - (vc.applied_amount or Decimal('0'))

        if not vc_id:
            db.session.add(vc)
            db.session.flush()

        for line_item in line_items:
            line_item.vendor_credit_id = vc.id
            db.session.add(line_item)

        db.session.commit()
        flash('Vendor credit saved!', 'success')
        return redirect(url_for('vendor_credits.view', id=vc.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('vendor_credits.create'))


@vendor_credits_bp.route('/view/<int:id>')
@login_required
def view(id):
    """View vendor credit"""
    vc = VendorCredit.query.filter(
        VendorCredit.id == id,
        VendorCredit.organization_id == current_user.organization_id
    ).first_or_404()

    open_bills = Bill.query.filter(
        Bill.organization_id == current_user.organization_id,
        Bill.vendor_id == vc.vendor_id,
        Bill.status.in_([BillStatus.RECEIVED, BillStatus.PARTIAL, BillStatus.OVERDUE]),
        Bill.balance > 0
    ).all()

    return render_template('vendor_credits/view.html',
                         vendor_credit=vc,
                         open_bills=open_bills,
                         VendorCreditStatus=VendorCreditStatus)


@vendor_credits_bp.route('/open/<int:id>', methods=['POST'])
@login_required
def open_vendor_credit(id):
    """Open a draft vendor credit"""
    vc = VendorCredit.query.filter(
        VendorCredit.id == id,
        VendorCredit.organization_id == current_user.organization_id
    ).first_or_404()

    if vc.status != VendorCreditStatus.DRAFT:
        flash('Only draft vendor credits can be opened.', 'error')
        return redirect(url_for('vendor_credits.view', id=id))

    try:
        vc.status = VendorCreditStatus.OPEN

        accounts_payable = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.LIABILITY,
            Account.name.ilike('%payable%')
        ).first()

        expense_account = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.EXPENSE
        ).first()

        if accounts_payable and expense_account:
            entry = JournalEntry(
                organization_id=current_user.organization_id,
                entry_number=f"VC-{vc.credit_number}",
                date=vc.credit_date,
                description=f"Vendor Credit {vc.credit_number} - {vc.vendor.display_name}",
                source_type='vendor_credit',
                source_id=vc.id,
                created_by=current_user.id,
                debit_total=vc.total,
                credit_total=vc.total
            )
            db.session.add(entry)
            db.session.flush()

            # Debit AP (reduce what we owe)
            db.session.add(JournalLineItem(
                journal_entry_id=entry.id,
                account_id=accounts_payable.id,
                description=f"Vendor Credit {vc.credit_number}",
                debit=vc.total,
                credit=Decimal('0.00'),
                contact_type='vendor',
                contact_id=vc.vendor_id
            ))
            # Credit expense (reduce expense)
            db.session.add(JournalLineItem(
                journal_entry_id=entry.id,
                account_id=expense_account.id,
                description=f"Vendor Credit {vc.credit_number}",
                debit=Decimal('0.00'),
                credit=vc.total,
                contact_type='vendor',
                contact_id=vc.vendor_id
            ))

        db.session.commit()
        flash('Vendor credit opened!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('vendor_credits.view', id=id))


@vendor_credits_bp.route('/apply/<int:id>', methods=['POST'])
@login_required
def apply_to_bill(id):
    """Apply vendor credit to a bill"""
    vc = VendorCredit.query.filter(
        VendorCredit.id == id,
        VendorCredit.organization_id == current_user.organization_id
    ).first_or_404()

    if vc.status not in [VendorCreditStatus.OPEN, VendorCreditStatus.PARTIAL]:
        flash('This vendor credit cannot be applied.', 'error')
        return redirect(url_for('vendor_credits.view', id=id))

    try:
        bill_id = request.form.get('bill_id')
        apply_amount = Decimal(request.form.get('apply_amount', '0'))

        bill = Bill.query.filter(
            Bill.id == bill_id,
            Bill.organization_id == current_user.organization_id
        ).first_or_404()

        if apply_amount <= 0 or apply_amount > vc.balance or apply_amount > bill.balance:
            flash('Invalid application amount.', 'error')
            return redirect(url_for('vendor_credits.view', id=id))

        application = VendorCreditApplication(
            vendor_credit_id=vc.id,
            bill_id=bill.id,
            applied_amount=apply_amount,
            applied_date=date.today()
        )
        db.session.add(application)

        vc.applied_amount = (vc.applied_amount or Decimal('0')) + apply_amount
        vc.balance = vc.total - vc.applied_amount
        if vc.balance <= 0:
            vc.status = VendorCreditStatus.CLOSED
        else:
            vc.status = VendorCreditStatus.PARTIAL

        bill.paid_amount = (bill.paid_amount or Decimal('0')) + apply_amount
        bill.balance = bill.total - bill.paid_amount
        if bill.balance <= 0:
            bill.status = BillStatus.PAID
        else:
            bill.status = BillStatus.PARTIAL

        db.session.commit()
        flash(f'Applied {apply_amount} to Bill {bill.bill_number}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('vendor_credits.view', id=id))


@vendor_credits_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete vendor credit"""
    vc = VendorCredit.query.filter(
        VendorCredit.id == id,
        VendorCredit.organization_id == current_user.organization_id
    ).first_or_404()

    if vc.status != VendorCreditStatus.DRAFT:
        flash('Only draft vendor credits can be deleted.', 'error')
        return redirect(url_for('vendor_credits.view', id=id))

    try:
        db.session.delete(vc)
        db.session.commit()
        flash('Vendor credit deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('vendor_credits.index'))
