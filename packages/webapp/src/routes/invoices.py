"""
Invoice management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import desc, func, and_, or_

from packages.server.src.models import (
    Invoice, InvoiceLineItem, Customer, Item, Account, AccountType, 
    InvoiceStatus, JournalEntry, JournalLineItem
)
from packages.server.src.database import db

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('/')
@login_required
def index():
    """List all invoices with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    customer_filter = request.args.get('customer', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    search = request.args.get('search', '')
    
    # Build query
    query = Invoice.query.filter(Invoice.organization_id == current_user.organization_id)
    
    # Apply filters
    if status_filter:
        query = query.filter(Invoice.status == status_filter)
    
    if customer_filter:
        query = query.filter(Invoice.customer_id == customer_filter)
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date <= to_date)
        except ValueError:
            pass
    
    if search:
        query = query.join(Customer).filter(
            or_(
                Invoice.invoice_number.ilike(f'%{search}%'),
                Invoice.reference.ilike(f'%{search}%'),
                Customer.display_name.ilike(f'%{search}%')
            )
        )
    
    # Order by invoice date (newest first)
    query = query.order_by(desc(Invoice.invoice_date), desc(Invoice.id))
    
    # Paginate
    invoices = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get customers for filter dropdown
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()
    
    # Get summary statistics
    total_invoices = Invoice.query.filter(
        Invoice.organization_id == current_user.organization_id
    ).count()
    
    total_amount = db.session.query(func.sum(Invoice.total)).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.status != InvoiceStatus.CANCELLED
    ).scalar() or Decimal('0.00')
    
    paid_amount = db.session.query(func.sum(Invoice.paid_amount)).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.status != InvoiceStatus.CANCELLED
    ).scalar() or Decimal('0.00')
    
    outstanding_amount = db.session.query(func.sum(Invoice.balance)).filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.balance > 0,
        Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE])
    ).scalar() or Decimal('0.00')
    
    stats = {
        'total_invoices': total_invoices,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'outstanding_amount': outstanding_amount
    }
    
    return render_template('invoices/index.html', 
                         invoices=invoices, 
                         customers=customers,
                         stats=stats,
                         InvoiceStatus=InvoiceStatus,
                         today=date.today())

@invoices_bp.route('/create')
@login_required
def create():
    """Show invoice creation form"""
    # Get customers
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()
    
    # Get items
    items = Item.query.filter(
        Item.organization_id == current_user.organization_id,
        Item.is_active == True
    ).order_by(Item.name).all()
    
    # Generate next invoice number
    last_invoice = Invoice.query.filter(
        Invoice.organization_id == current_user.organization_id
    ).order_by(desc(Invoice.id)).first()
    
    if last_invoice:
        # Extract number from last invoice and increment
        try:
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            next_number = f"INV-{last_num + 1:04d}"
        except (ValueError, IndexError):
            next_number = f"INV-{Invoice.query.filter(Invoice.organization_id == current_user.organization_id).count() + 1:04d}"
    else:
        next_number = "INV-0001"
    
    # Get default accounts
    sales_account = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.INCOME,
        Account.name.ilike('%sales%')
    ).first()
    
    return render_template('invoices/create.html', 
                         customers=customers,
                         items=items,
                         next_number=next_number,
                         sales_account=sales_account)

@invoices_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save new or updated invoice"""
    try:
        invoice_id = request.form.get('invoice_id')
        
        # Get form data
        customer_id = request.form.get('customer_id')
        invoice_number = request.form.get('invoice_number')
        invoice_date = request.form.get('invoice_date')
        due_date = request.form.get('due_date')
        reference = request.form.get('reference', '')
        terms = request.form.get('terms', '')
        notes = request.form.get('notes', '')
        
        # Validate required fields
        if not all([customer_id, invoice_number, invoice_date, due_date]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('invoices.create'))
        
        # Convert dates
        try:
            invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').date()
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'error')
            return redirect(url_for('invoices.create'))
        
        # Check if invoice number exists (for new invoices)
        if not invoice_id:
            existing = Invoice.query.filter(
                Invoice.organization_id == current_user.organization_id,
                Invoice.invoice_number == invoice_number
            ).first()
            if existing:
                flash('Invoice number already exists.', 'error')
                return redirect(url_for('invoices.create'))
        
        # Create or update invoice
        if invoice_id:
            invoice = Invoice.query.get_or_404(invoice_id)
            if invoice.organization_id != current_user.organization_id:
                flash('Invoice not found.', 'error')
                return redirect(url_for('invoices.index'))
        else:
            invoice = Invoice(
                organization_id=current_user.organization_id,
                invoice_number=invoice_number
            )
        
        # Update invoice fields
        invoice.customer_id = customer_id
        invoice.invoice_date = invoice_date
        invoice.due_date = due_date
        invoice.reference = reference
        invoice.terms = terms
        invoice.notes = notes
        
        # Process line items
        item_ids = request.form.getlist('item_id[]')
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        rates = request.form.getlist('rate[]')
        
        # Clear existing line items if updating
        if invoice_id:
            InvoiceLineItem.query.filter(InvoiceLineItem.invoice_id == invoice.id).delete()
        
        subtotal = Decimal('0.00')
        line_items = []
        
        for i in range(len(descriptions)):
            if descriptions[i].strip():  # Only add non-empty items
                try:
                    quantity = Decimal(quantities[i] or '0')
                    rate = Decimal(rates[i] or '0')
                    amount = quantity * rate
                    
                    line_item = InvoiceLineItem(
                        item_id=item_ids[i] if item_ids[i] else None,
                        description=descriptions[i],
                        quantity=quantity,
                        rate=rate,
                        amount=amount
                    )
                    line_items.append(line_item)
                    subtotal += amount
                except (ValueError, TypeError):
                    continue
        
        if not line_items:
            flash('Please add at least one line item.', 'error')
            return redirect(url_for('invoices.create'))
        
        # Calculate totals (simplified - no tax for now)
        tax_amount = Decimal('0.00')
        discount_amount = Decimal('0.00')
        total = subtotal + tax_amount - discount_amount
        
        invoice.subtotal = subtotal
        invoice.tax_amount = tax_amount
        invoice.discount_amount = discount_amount
        invoice.total = total
        invoice.balance = total
        
        # Save invoice
        if not invoice_id:
            db.session.add(invoice)
            db.session.flush()  # Get the ID
        
        # Add line items
        for line_item in line_items:
            line_item.invoice_id = invoice.id
            db.session.add(line_item)
        
        db.session.commit()
        
        flash('Invoice saved successfully!', 'success')
        return redirect(url_for('invoices.view', id=invoice.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving invoice: {str(e)}', 'error')
        return redirect(url_for('invoices.create'))

@invoices_bp.route('/view/<int:id>')
@login_required
def view(id):
    """View invoice details"""
    invoice = Invoice.query.filter(
        Invoice.id == id,
        Invoice.organization_id == current_user.organization_id
    ).first_or_404()
    
    return render_template('invoices/view.html', invoice=invoice, InvoiceStatus=InvoiceStatus)

@invoices_bp.route('/edit/<int:id>')
@login_required
def edit(id):
    """Edit invoice"""
    invoice = Invoice.query.filter(
        Invoice.id == id,
        Invoice.organization_id == current_user.organization_id
    ).first_or_404()
    
    # Only allow editing of draft invoices
    if invoice.status != InvoiceStatus.DRAFT:
        flash('Only draft invoices can be edited.', 'error')
        return redirect(url_for('invoices.view', id=id))
    
    # Get customers and items
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()
    
    items = Item.query.filter(
        Item.organization_id == current_user.organization_id,
        Item.is_active == True
    ).order_by(Item.name).all()
    
    return render_template('invoices/edit.html', 
                         invoice=invoice,
                         customers=customers,
                         items=items)

@invoices_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete invoice"""
    invoice = Invoice.query.filter(
        Invoice.id == id,
        Invoice.organization_id == current_user.organization_id
    ).first_or_404()
    
    # Only allow deletion of draft invoices
    if invoice.status != InvoiceStatus.DRAFT:
        flash('Only draft invoices can be deleted.', 'error')
        return redirect(url_for('invoices.view', id=id))
    
    try:
        db.session.delete(invoice)
        db.session.commit()
        flash('Invoice deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting invoice: {str(e)}', 'error')
    
    return redirect(url_for('invoices.index'))

@invoices_bp.route('/send/<int:id>', methods=['POST'])
@login_required
def send(id):
    """Send invoice to customer"""
    invoice = Invoice.query.filter(
        Invoice.id == id,
        Invoice.organization_id == current_user.organization_id
    ).first_or_404()
    
    if invoice.status != InvoiceStatus.DRAFT:
        flash('Only draft invoices can be sent.', 'error')
        return redirect(url_for('invoices.view', id=id))
    
    try:
        # Update status
        invoice.status = InvoiceStatus.SENT
        
        # Create journal entry for the invoice
        create_invoice_journal_entry(invoice)
        
        db.session.commit()
        flash('Invoice sent successfully!', 'success')
        
        # TODO: Send email to customer
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error sending invoice: {str(e)}', 'error')
    
    return redirect(url_for('invoices.view', id=id))

def create_invoice_journal_entry(invoice):
    """Create accounting journal entry for an invoice"""
    # Get accounts
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
    
    if not accounts_receivable or not sales_account:
        raise Exception("Required accounts not found. Please set up Accounts Receivable and Sales accounts.")
    
    # Create journal entry
    entry = JournalEntry(
        organization_id=current_user.organization_id,
        entry_number=f"INV-{invoice.invoice_number}",
        date=invoice.invoice_date,
        description=f"Invoice {invoice.invoice_number} - {invoice.customer.display_name}",
        source_type='invoice',
        source_id=invoice.id,
        created_by=current_user.id,
        debit_total=invoice.total,
        credit_total=invoice.total
    )
    db.session.add(entry)
    db.session.flush()
    
    # Debit Accounts Receivable
    debit_line = JournalLineItem(
        journal_entry_id=entry.id,
        account_id=accounts_receivable.id,
        description=f"Invoice {invoice.invoice_number}",
        debit=invoice.total,
        credit=Decimal('0.00'),
        contact_type='customer',
        contact_id=invoice.customer_id
    )
    db.session.add(debit_line)
    
    # Credit Sales
    credit_line = JournalLineItem(
        journal_entry_id=entry.id,
        account_id=sales_account.id,
        description=f"Sales - Invoice {invoice.invoice_number}",
        debit=Decimal('0.00'),
        credit=invoice.total
    )
    db.session.add(credit_line)

@invoices_bp.route('/mark-paid/<int:id>', methods=['POST'])
@login_required
def mark_paid(id):
    """Mark invoice as paid"""
    invoice = Invoice.query.filter(
        Invoice.id == id,
        Invoice.organization_id == current_user.organization_id
    ).first_or_404()
    
    if invoice.status not in [InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE]:
        flash('Invoice cannot be marked as paid.', 'error')
        return redirect(url_for('invoices.view', id=id))
    
    try:
        # Mark as fully paid
        invoice.paid_amount = invoice.total
        invoice.balance = Decimal('0.00')
        invoice.status = InvoiceStatus.PAID
        
        db.session.commit()
        flash('Invoice marked as paid!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating invoice: {str(e)}', 'error')
    
    return redirect(url_for('invoices.view', id=id))

@invoices_bp.route('/api/items/<int:item_id>')
@login_required
def get_item_details(item_id):
    """Get item details for invoice line items (AJAX)"""
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
        'sell_price': str(item.sell_price),
        'unit': item.unit
    })
