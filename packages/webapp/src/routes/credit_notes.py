"""
Credit Note management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import desc, func, or_

from packages.server.src.models import (
    CreditNote, CreditNoteLineItem, CreditNoteApplication,
    Customer, Item, Invoice, InvoiceStatus, Account, AccountType,
    CreditNoteStatus, JournalEntry, JournalLineItem, TaxCode
)
from packages.server.src.database import db

credit_notes_bp = Blueprint('credit_notes', __name__)


@credit_notes_bp.route('/')
@login_required
def index():
    """List all credit notes"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    customer_filter = request.args.get('customer', '')

    query = CreditNote.query.filter(CreditNote.organization_id == current_user.organization_id)

    if status_filter:
        query = query.filter(CreditNote.status == status_filter)
    if customer_filter:
        query = query.filter(CreditNote.customer_id == customer_filter)

    query = query.order_by(desc(CreditNote.credit_note_date), desc(CreditNote.id))
    credit_notes = query.paginate(page=page, per_page=per_page, error_out=False)

    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()

    total_amount = db.session.query(func.sum(CreditNote.total)).filter(
        CreditNote.organization_id == current_user.organization_id,
        CreditNote.status != CreditNoteStatus.CANCELLED
    ).scalar() or Decimal('0.00')

    open_amount = db.session.query(func.sum(CreditNote.balance)).filter(
        CreditNote.organization_id == current_user.organization_id,
        CreditNote.status.in_([CreditNoteStatus.OPEN, CreditNoteStatus.PARTIAL])
    ).scalar() or Decimal('0.00')

    stats = {
        'total_count': CreditNote.query.filter(CreditNote.organization_id == current_user.organization_id).count(),
        'total_amount': total_amount,
        'open_amount': open_amount
    }

    return render_template('credit_notes/index.html',
                         credit_notes=credit_notes,
                         customers=customers,
                         stats=stats,
                         CreditNoteStatus=CreditNoteStatus)


@credit_notes_bp.route('/create')
@login_required
def create():
    """Show credit note creation form"""
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()

    items = Item.query.filter(
        Item.organization_id == current_user.organization_id,
        Item.is_active == True
    ).order_by(Item.name).all()

    tax_codes = TaxCode.query.filter(
        TaxCode.organization_id == current_user.organization_id,
        TaxCode.is_active == True
    ).all()

    last_cn = CreditNote.query.filter(
        CreditNote.organization_id == current_user.organization_id
    ).order_by(desc(CreditNote.id)).first()

    if last_cn:
        try:
            last_num = int(last_cn.credit_note_number.split('-')[-1])
            next_number = f"CN-{last_num + 1:04d}"
        except (ValueError, IndexError):
            next_number = f"CN-{CreditNote.query.filter(CreditNote.organization_id == current_user.organization_id).count() + 1:04d}"
    else:
        next_number = "CN-0001"

    # Pre-select invoice if provided
    invoice_id = request.args.get('invoice_id')
    selected_invoice = None
    if invoice_id:
        selected_invoice = Invoice.query.filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id
        ).first()

    return render_template('credit_notes/create.html',
                         customers=customers,
                         items=items,
                         tax_codes=tax_codes,
                         next_number=next_number,
                         selected_invoice=selected_invoice,
                         today=date.today())


@credit_notes_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save credit note"""
    try:
        cn_id = request.form.get('credit_note_id')
        customer_id = request.form.get('customer_id')
        credit_note_number = request.form.get('credit_note_number')
        credit_note_date = request.form.get('credit_note_date')
        invoice_id = request.form.get('invoice_id') or None
        reference = request.form.get('reference', '')
        notes = request.form.get('notes', '')

        if not all([customer_id, credit_note_number, credit_note_date]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('credit_notes.create'))

        credit_note_date = datetime.strptime(credit_note_date, '%Y-%m-%d').date()

        if cn_id:
            cn = CreditNote.query.get_or_404(cn_id)
            if cn.organization_id != current_user.organization_id:
                flash('Credit note not found.', 'error')
                return redirect(url_for('credit_notes.index'))
        else:
            cn = CreditNote(
                organization_id=current_user.organization_id,
                credit_note_number=credit_note_number
            )

        cn.customer_id = customer_id
        cn.credit_note_date = credit_note_date
        cn.invoice_id = invoice_id
        cn.reference = reference
        cn.notes = notes

        # Process line items
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        rates = request.form.getlist('rate[]')
        item_ids = request.form.getlist('item_id[]')
        tax_code_ids = request.form.getlist('tax_code_id[]')

        if cn_id:
            CreditNoteLineItem.query.filter(CreditNoteLineItem.credit_note_id == cn.id).delete()

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

                    line_item = CreditNoteLineItem(
                        item_id=item_ids[i] if i < len(item_ids) and item_ids[i] else None,
                        description=descriptions[i],
                        quantity=quantity,
                        rate=rate,
                        amount=amount,
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
            return redirect(url_for('credit_notes.create'))

        cn.subtotal = subtotal
        cn.tax_amount = total_tax
        cn.total = subtotal + total_tax
        cn.balance = cn.total - (cn.applied_amount or Decimal('0'))

        if not cn_id:
            db.session.add(cn)
            db.session.flush()

        for line_item in line_items:
            line_item.credit_note_id = cn.id
            db.session.add(line_item)

        db.session.commit()
        flash('Credit note saved successfully!', 'success')
        return redirect(url_for('credit_notes.view', id=cn.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error saving credit note: {str(e)}', 'error')
        return redirect(url_for('credit_notes.create'))


@credit_notes_bp.route('/view/<int:id>')
@login_required
def view(id):
    """View credit note"""
    cn = CreditNote.query.filter(
        CreditNote.id == id,
        CreditNote.organization_id == current_user.organization_id
    ).first_or_404()

    # Get open invoices for this customer (for applying credit)
    open_invoices = Invoice.query.filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.customer_id == cn.customer_id,
        Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE]),
        Invoice.balance > 0
    ).all()

    return render_template('credit_notes/view.html',
                         credit_note=cn,
                         open_invoices=open_invoices,
                         CreditNoteStatus=CreditNoteStatus)


@credit_notes_bp.route('/open/<int:id>', methods=['POST'])
@login_required
def open_credit_note(id):
    """Open a draft credit note"""
    cn = CreditNote.query.filter(
        CreditNote.id == id,
        CreditNote.organization_id == current_user.organization_id
    ).first_or_404()

    if cn.status != CreditNoteStatus.DRAFT:
        flash('Only draft credit notes can be opened.', 'error')
        return redirect(url_for('credit_notes.view', id=id))

    try:
        cn.status = CreditNoteStatus.OPEN

        # Create journal entry: Debit Sales Returns, Credit AR
        accounts_receivable = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.ASSET,
            Account.name.ilike('%receivable%')
        ).first()

        sales_account = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.INCOME,
            Account.name.ilike('%sales%')
        ).first()

        if accounts_receivable and sales_account:
            entry = JournalEntry(
                organization_id=current_user.organization_id,
                entry_number=f"CN-{cn.credit_note_number}",
                date=cn.credit_note_date,
                description=f"Credit Note {cn.credit_note_number} - {cn.customer.display_name}",
                source_type='credit_note',
                source_id=cn.id,
                created_by=current_user.id,
                debit_total=cn.total,
                credit_total=cn.total
            )
            db.session.add(entry)
            db.session.flush()

            db.session.add(JournalLineItem(
                journal_entry_id=entry.id,
                account_id=sales_account.id,
                description=f"Credit Note {cn.credit_note_number}",
                debit=cn.total,
                credit=Decimal('0.00'),
                contact_type='customer',
                contact_id=cn.customer_id
            ))
            db.session.add(JournalLineItem(
                journal_entry_id=entry.id,
                account_id=accounts_receivable.id,
                description=f"Credit Note {cn.credit_note_number}",
                debit=Decimal('0.00'),
                credit=cn.total,
                contact_type='customer',
                contact_id=cn.customer_id
            ))

        db.session.commit()
        flash('Credit note opened!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('credit_notes.view', id=id))


@credit_notes_bp.route('/apply/<int:id>', methods=['POST'])
@login_required
def apply_to_invoice(id):
    """Apply credit note to an invoice"""
    cn = CreditNote.query.filter(
        CreditNote.id == id,
        CreditNote.organization_id == current_user.organization_id
    ).first_or_404()

    if cn.status not in [CreditNoteStatus.OPEN, CreditNoteStatus.PARTIAL]:
        flash('This credit note cannot be applied.', 'error')
        return redirect(url_for('credit_notes.view', id=id))

    try:
        invoice_id = request.form.get('invoice_id')
        apply_amount = Decimal(request.form.get('apply_amount', '0'))

        invoice = Invoice.query.filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id
        ).first_or_404()

        if apply_amount <= 0 or apply_amount > cn.balance or apply_amount > invoice.balance:
            flash('Invalid application amount.', 'error')
            return redirect(url_for('credit_notes.view', id=id))

        application = CreditNoteApplication(
            credit_note_id=cn.id,
            invoice_id=invoice.id,
            applied_amount=apply_amount,
            applied_date=date.today()
        )
        db.session.add(application)

        cn.applied_amount = (cn.applied_amount or Decimal('0')) + apply_amount
        cn.balance = cn.total - cn.applied_amount
        if cn.balance <= 0:
            cn.status = CreditNoteStatus.CLOSED
        else:
            cn.status = CreditNoteStatus.PARTIAL

        invoice.paid_amount = (invoice.paid_amount or Decimal('0')) + apply_amount
        invoice.balance = invoice.total - invoice.paid_amount
        if invoice.balance <= 0:
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = InvoiceStatus.PARTIAL

        db.session.commit()
        flash(f'Applied {apply_amount} to Invoice {invoice.invoice_number}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('credit_notes.view', id=id))


@credit_notes_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete credit note"""
    cn = CreditNote.query.filter(
        CreditNote.id == id,
        CreditNote.organization_id == current_user.organization_id
    ).first_or_404()

    if cn.status != CreditNoteStatus.DRAFT:
        flash('Only draft credit notes can be deleted.', 'error')
        return redirect(url_for('credit_notes.view', id=id))

    try:
        db.session.delete(cn)
        db.session.commit()
        flash('Credit note deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('credit_notes.index'))
