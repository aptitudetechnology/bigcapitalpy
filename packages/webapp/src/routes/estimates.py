"""
Sale Estimate management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import desc, func, or_

from packages.server.src.models import (
    Estimate, EstimateLineItem, EstimateStatus,
    Invoice, InvoiceLineItem, InvoiceStatus,
    Customer, Item, Account, AccountType, TaxCode
)
from packages.server.src.database import db

estimates_bp = Blueprint('estimates', __name__, url_prefix='/estimates')


@estimates_bp.route('/')
@login_required
def index():
    """List all estimates"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    customer_filter = request.args.get('customer', '')
    search = request.args.get('search', '')

    query = Estimate.query.filter(Estimate.organization_id == current_user.organization_id)

    if status_filter:
        query = query.filter(Estimate.status == status_filter)
    if customer_filter:
        query = query.filter(Estimate.customer_id == customer_filter)
    if search:
        query = query.join(Customer).filter(
            or_(
                Estimate.estimate_number.ilike(f'%{search}%'),
                Estimate.reference.ilike(f'%{search}%'),
                Customer.display_name.ilike(f'%{search}%')
            )
        )

    query = query.order_by(desc(Estimate.estimate_date), desc(Estimate.id))
    estimates = query.paginate(page=page, per_page=per_page, error_out=False)

    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()

    total_count = Estimate.query.filter(
        Estimate.organization_id == current_user.organization_id
    ).count()

    total_amount = db.session.query(func.sum(Estimate.total)).filter(
        Estimate.organization_id == current_user.organization_id,
        Estimate.status != EstimateStatus.CANCELLED
    ).scalar() or Decimal('0.00')

    approved_amount = db.session.query(func.sum(Estimate.total)).filter(
        Estimate.organization_id == current_user.organization_id,
        Estimate.status == EstimateStatus.APPROVED
    ).scalar() or Decimal('0.00')

    stats = {
        'total_count': total_count,
        'total_amount': total_amount,
        'approved_amount': approved_amount
    }

    return render_template('estimates/index.html',
                         estimates=estimates,
                         customers=customers,
                         stats=stats,
                         EstimateStatus=EstimateStatus)


@estimates_bp.route('/create')
@login_required
def create():
    """Show estimate creation form"""
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

    last_estimate = Estimate.query.filter(
        Estimate.organization_id == current_user.organization_id
    ).order_by(desc(Estimate.id)).first()

    if last_estimate:
        try:
            last_num = int(last_estimate.estimate_number.split('-')[-1])
            next_number = f"EST-{last_num + 1:04d}"
        except (ValueError, IndexError):
            next_number = f"EST-{Estimate.query.filter(Estimate.organization_id == current_user.organization_id).count() + 1:04d}"
    else:
        next_number = "EST-0001"

    return render_template('estimates/create.html',
                         customers=customers,
                         items=items,
                         tax_codes=tax_codes,
                         next_number=next_number,
                         today=date.today())


@estimates_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save estimate"""
    try:
        estimate_id = request.form.get('estimate_id')
        customer_id = request.form.get('customer_id')
        estimate_number = request.form.get('estimate_number')
        estimate_date = request.form.get('estimate_date')
        expiry_date = request.form.get('expiry_date')
        reference = request.form.get('reference', '')
        terms = request.form.get('terms', '')
        notes = request.form.get('notes', '')

        if not all([customer_id, estimate_number, estimate_date]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('estimates.create'))

        estimate_date = datetime.strptime(estimate_date, '%Y-%m-%d').date()
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else estimate_date + timedelta(days=30)

        if not estimate_id:
            existing = Estimate.query.filter(
                Estimate.organization_id == current_user.organization_id,
                Estimate.estimate_number == estimate_number
            ).first()
            if existing:
                flash('Estimate number already exists.', 'error')
                return redirect(url_for('estimates.create'))

        if estimate_id:
            estimate = Estimate.query.get_or_404(estimate_id)
            if estimate.organization_id != current_user.organization_id:
                flash('Estimate not found.', 'error')
                return redirect(url_for('estimates.index'))
        else:
            estimate = Estimate(
                organization_id=current_user.organization_id,
                estimate_number=estimate_number
            )

        estimate.customer_id = customer_id
        estimate.estimate_date = estimate_date
        estimate.expiry_date = expiry_date
        estimate.reference = reference
        estimate.terms = terms
        estimate.notes = notes

        # Process line items
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        rates = request.form.getlist('rate[]')
        item_ids = request.form.getlist('item_id[]')
        tax_code_ids = request.form.getlist('tax_code_id[]')

        if estimate_id:
            EstimateLineItem.query.filter(EstimateLineItem.estimate_id == estimate.id).delete()

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

                    line_item = EstimateLineItem(
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
            return redirect(url_for('estimates.create'))

        estimate.subtotal = subtotal
        estimate.tax_amount = total_tax
        estimate.total = subtotal + total_tax

        if not estimate_id:
            db.session.add(estimate)
            db.session.flush()

        for line_item in line_items:
            line_item.estimate_id = estimate.id
            db.session.add(line_item)

        db.session.commit()
        flash('Estimate saved successfully!', 'success')
        return redirect(url_for('estimates.view', id=estimate.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error saving estimate: {str(e)}', 'error')
        return redirect(url_for('estimates.create'))


@estimates_bp.route('/view/<int:id>')
@login_required
def view(id):
    """View estimate"""
    estimate = Estimate.query.filter(
        Estimate.id == id,
        Estimate.organization_id == current_user.organization_id
    ).first_or_404()
    return render_template('estimates/view.html', estimate=estimate, EstimateStatus=EstimateStatus)


@estimates_bp.route('/edit/<int:id>')
@login_required
def edit(id):
    """Edit estimate"""
    estimate = Estimate.query.filter(
        Estimate.id == id,
        Estimate.organization_id == current_user.organization_id
    ).first_or_404()

    if estimate.status != EstimateStatus.DRAFT:
        flash('Only draft estimates can be edited.', 'error')
        return redirect(url_for('estimates.view', id=id))

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

    return render_template('estimates/edit.html',
                         estimate=estimate,
                         customers=customers,
                         items=items,
                         tax_codes=tax_codes)


@estimates_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete estimate"""
    estimate = Estimate.query.filter(
        Estimate.id == id,
        Estimate.organization_id == current_user.organization_id
    ).first_or_404()

    if estimate.status not in [EstimateStatus.DRAFT, EstimateStatus.REJECTED]:
        flash('This estimate cannot be deleted.', 'error')
        return redirect(url_for('estimates.view', id=id))

    try:
        db.session.delete(estimate)
        db.session.commit()
        flash('Estimate deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('estimates.index'))


@estimates_bp.route('/send/<int:id>', methods=['POST'])
@login_required
def send(id):
    """Mark estimate as sent"""
    estimate = Estimate.query.filter(
        Estimate.id == id,
        Estimate.organization_id == current_user.organization_id
    ).first_or_404()

    if estimate.status != EstimateStatus.DRAFT:
        flash('Only draft estimates can be sent.', 'error')
        return redirect(url_for('estimates.view', id=id))

    estimate.status = EstimateStatus.SENT
    db.session.commit()
    flash('Estimate marked as sent!', 'success')
    return redirect(url_for('estimates.view', id=id))


@estimates_bp.route('/approve/<int:id>', methods=['POST'])
@login_required
def approve(id):
    """Approve estimate"""
    estimate = Estimate.query.filter(
        Estimate.id == id,
        Estimate.organization_id == current_user.organization_id
    ).first_or_404()

    if estimate.status not in [EstimateStatus.DRAFT, EstimateStatus.SENT]:
        flash('This estimate cannot be approved.', 'error')
        return redirect(url_for('estimates.view', id=id))

    estimate.status = EstimateStatus.APPROVED
    db.session.commit()
    flash('Estimate approved!', 'success')
    return redirect(url_for('estimates.view', id=id))


@estimates_bp.route('/reject/<int:id>', methods=['POST'])
@login_required
def reject(id):
    """Reject estimate"""
    estimate = Estimate.query.filter(
        Estimate.id == id,
        Estimate.organization_id == current_user.organization_id
    ).first_or_404()

    if estimate.status not in [EstimateStatus.DRAFT, EstimateStatus.SENT]:
        flash('This estimate cannot be rejected.', 'error')
        return redirect(url_for('estimates.view', id=id))

    estimate.status = EstimateStatus.REJECTED
    db.session.commit()
    flash('Estimate rejected.', 'success')
    return redirect(url_for('estimates.view', id=id))


@estimates_bp.route('/convert-to-invoice/<int:id>', methods=['POST'])
@login_required
def convert_to_invoice(id):
    """Convert an approved estimate to an invoice"""
    estimate = Estimate.query.filter(
        Estimate.id == id,
        Estimate.organization_id == current_user.organization_id
    ).first_or_404()

    if estimate.status != EstimateStatus.APPROVED:
        flash('Only approved estimates can be converted to invoices.', 'error')
        return redirect(url_for('estimates.view', id=id))

    if estimate.converted_invoice_id:
        flash('This estimate has already been converted to an invoice.', 'error')
        return redirect(url_for('estimates.view', id=id))

    try:
        # Generate invoice number
        last_invoice = Invoice.query.filter(
            Invoice.organization_id == current_user.organization_id
        ).order_by(desc(Invoice.id)).first()

        if last_invoice:
            try:
                last_num = int(last_invoice.invoice_number.split('-')[-1])
                invoice_number = f"INV-{last_num + 1:04d}"
            except (ValueError, IndexError):
                invoice_number = f"INV-{Invoice.query.filter(Invoice.organization_id == current_user.organization_id).count() + 1:04d}"
        else:
            invoice_number = "INV-0001"

        # Create invoice from estimate
        invoice = Invoice(
            organization_id=current_user.organization_id,
            invoice_number=invoice_number,
            customer_id=estimate.customer_id,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            reference=f"From Estimate {estimate.estimate_number}",
            subtotal=estimate.subtotal,
            tax_amount=estimate.tax_amount,
            total=estimate.total,
            balance=estimate.total,
            currency=estimate.currency,
            status=InvoiceStatus.DRAFT,
            terms=estimate.terms,
            notes=estimate.notes
        )
        db.session.add(invoice)
        db.session.flush()

        # Copy line items
        for est_line in estimate.line_items:
            inv_line = InvoiceLineItem(
                invoice_id=invoice.id,
                item_id=est_line.item_id,
                description=est_line.description,
                quantity=est_line.quantity,
                rate=est_line.rate,
                amount=est_line.amount,
                tax_rate=est_line.tax_rate,
                tax_amount=est_line.tax_amount,
                tax_code_id=est_line.tax_code_id
            )
            db.session.add(inv_line)

        # Update estimate
        estimate.status = EstimateStatus.INVOICED
        estimate.converted_invoice_id = invoice.id

        db.session.commit()
        flash(f'Invoice {invoice_number} created from estimate!', 'success')
        return redirect(url_for('invoices.view', id=invoice.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error converting estimate: {str(e)}', 'error')
        return redirect(url_for('estimates.view', id=id))
