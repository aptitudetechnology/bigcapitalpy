"""
Payments Received routes for BigCapitalPy
Handle customer payments and allocation to invoices
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import desc, func, and_, or_

from packages.server.src.models import (
    Payment, PaymentAllocation, PaymentMethod, Customer, Invoice, 
    Account, AccountType, InvoiceStatus, JournalEntry, JournalLineItem
)
from packages.server.src.database import db

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/')
@login_required
def index():
    """List all payments received with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    customer_filter = request.args.get('customer', '')
    method_filter = request.args.get('method', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    search = request.args.get('search', '')
    
    # Build query
    query = Payment.query.filter(Payment.organization_id == current_user.organization_id)
    
    # Apply filters
    if customer_filter:
        query = query.filter(Payment.customer_id == customer_filter)
    
    if method_filter:
        query = query.filter(Payment.payment_method == method_filter)
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Payment.payment_date >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Payment.payment_date <= to_date)
        except ValueError:
            pass
    
    if search:
        query = query.join(Customer).filter(
            or_(
                Payment.payment_number.ilike(f'%{search}%'),
                Payment.reference.ilike(f'%{search}%'),
                Customer.display_name.ilike(f'%{search}%')
            )
        )
    
    # Order by payment date (newest first)
    query = query.order_by(desc(Payment.payment_date), desc(Payment.id))
    
    # Paginate
    payments = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get customers for filter dropdown
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()
    
    # Calculate stats
    total_payments = Payment.query.filter(
        Payment.organization_id == current_user.organization_id
    ).with_entities(func.sum(Payment.amount)).scalar() or 0
    
    payments_this_month = Payment.query.filter(
        Payment.organization_id == current_user.organization_id,
        Payment.payment_date >= date.today().replace(day=1)
    ).with_entities(func.sum(Payment.amount)).scalar() or 0
    
    stats = {
        'total_payments': total_payments,
        'payments_this_month': payments_this_month,
        'total_count': Payment.query.filter(
            Payment.organization_id == current_user.organization_id
        ).count()
    }
    
    return render_template('payments/index.html',
                         payments=payments,
                         customers=customers,
                         stats=stats,
                         PaymentMethod=PaymentMethod,
                         today=date.today())

@payments_bp.route('/create')
@login_required
def create():
    """Show payment creation form"""
    # Get customers with outstanding invoices
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()
    
    # Get deposit accounts (cash/bank accounts)
    deposit_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        Account.is_active == True,
        or_(
            Account.name.ilike('%cash%'),
            Account.name.ilike('%bank%'),
            Account.name.ilike('%checking%'),
            Account.name.ilike('%savings%')
        )
    ).order_by(Account.name).all()
    
    # If no specific deposit accounts found, get all asset accounts
    if not deposit_accounts:
        deposit_accounts = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.ASSET,
            Account.is_active == True
        ).order_by(Account.name).all()
    
    # Generate next payment number
    last_payment = Payment.query.filter(
        Payment.organization_id == current_user.organization_id
    ).order_by(desc(Payment.id)).first()
    
    if last_payment:
        try:
            last_num = int(last_payment.payment_number.split('-')[-1])
            next_number = f"PMT-{last_num + 1:05d}"
        except (ValueError, IndexError):
            next_number = f"PMT-{Payment.query.filter(Payment.organization_id == current_user.organization_id).count() + 1:05d}"
    else:
        next_number = "PMT-00001"
    
    return render_template('payments/create.html',
                         customers=customers,
                         deposit_accounts=deposit_accounts,
                         next_number=next_number,
                         PaymentMethod=PaymentMethod,
                         today=date.today())

@payments_bp.route('/customer/<int:customer_id>/invoices')
@login_required
def get_customer_invoices(customer_id):
    """Get outstanding invoices for a customer (AJAX endpoint)"""
    invoices = Invoice.query.filter(
        Invoice.organization_id == current_user.organization_id,
        Invoice.customer_id == customer_id,
        Invoice.balance > 0,
        Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE])
    ).order_by(Invoice.invoice_date).all()
    
    invoice_data = []
    for invoice in invoices:
        invoice_data.append({
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
            'due_date': invoice.due_date.strftime('%Y-%m-%d'),
            'total': float(invoice.total),
            'paid_amount': float(invoice.paid_amount or 0),
            'balance': float(invoice.balance),
            'status': invoice.status.value
        })
    
    return jsonify({'invoices': invoice_data})

@payments_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save new payment"""
    try:
        # Get form data
        customer_id = request.form.get('customer_id')
        payment_number = request.form.get('payment_number')
        payment_date = request.form.get('payment_date')
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        deposit_account_id = request.form.get('deposit_account_id')
        reference = request.form.get('reference', '')
        notes = request.form.get('notes', '')
        bank_name = request.form.get('bank_name', '')
        check_number = request.form.get('check_number', '')
        
        # Validate required fields
        if not all([customer_id, payment_number, payment_date, amount, payment_method, deposit_account_id]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('payments.create'))
        
        # Convert and validate data
        try:
            payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            amount = Decimal(amount)
            payment_method_enum = PaymentMethod(payment_method)
        except (ValueError, TypeError):
            flash('Invalid data format.', 'error')
            return redirect(url_for('payments.create'))
        
        if amount <= 0:
            flash('Payment amount must be greater than zero.', 'error')
            return redirect(url_for('payments.create'))
        
        # Check if payment number exists
        existing = Payment.query.filter(
            Payment.organization_id == current_user.organization_id,
            Payment.payment_number == payment_number
        ).first()
        if existing:
            flash('Payment number already exists.', 'error')
            return redirect(url_for('payments.create'))
        
        # Create payment
        payment = Payment(
            payment_number=payment_number,
            payment_date=payment_date,
            amount=amount,
            payment_method=payment_method_enum,
            reference=reference,
            notes=notes,
            bank_name=bank_name,
            check_number=check_number,
            customer_id=customer_id,
            deposit_account_id=deposit_account_id,
            organization_id=current_user.organization_id,
            created_by=current_user.id
        )
        
        db.session.add(payment)
        db.session.flush()  # Get payment ID
        
        # Handle invoice allocations
        allocations_data = request.form.getlist('allocations')
        total_allocated = Decimal('0.00')
        
        for allocation_str in allocations_data:
            if allocation_str:
                try:
                    invoice_id, allocated_amount = allocation_str.split(':')
                    invoice_id = int(invoice_id)
                    allocated_amount = Decimal(allocated_amount)
                    
                    if allocated_amount > 0:
                        # Validate invoice exists and belongs to customer
                        invoice = Invoice.query.filter(
                            Invoice.id == invoice_id,
                            Invoice.customer_id == customer_id,
                            Invoice.organization_id == current_user.organization_id
                        ).first()
                        
                        if not invoice:
                            continue
                        
                        # Don't allocate more than the invoice balance
                        allocated_amount = min(allocated_amount, invoice.balance)
                        
                        if allocated_amount > 0:
                            allocation = PaymentAllocation(
                                payment_id=payment.id,
                                invoice_id=invoice_id,
                                allocated_amount=allocated_amount
                            )
                            db.session.add(allocation)
                            
                            # Update invoice paid amount and balance
                            invoice.paid_amount = (invoice.paid_amount or 0) + allocated_amount
                            invoice.balance = invoice.total - invoice.paid_amount
                            
                            # Update invoice status
                            if invoice.balance <= 0:
                                invoice.status = InvoiceStatus.PAID
                            elif invoice.paid_amount > 0:
                                invoice.status = InvoiceStatus.PARTIAL
                            
                            total_allocated += allocated_amount
                            
                except (ValueError, TypeError):
                    continue
        
        # Create journal entry for the payment
        create_payment_journal_entry(payment, total_allocated)
        
        db.session.commit()
        
        flash(f'Payment {payment_number} created successfully.', 'success')
        return redirect(url_for('payments.view', id=payment.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating payment: {str(e)}', 'error')
        return redirect(url_for('payments.create'))

@payments_bp.route('/<int:id>')
@login_required
def view(id):
    """View payment details"""
    payment = Payment.query.filter(
        Payment.id == id,
        Payment.organization_id == current_user.organization_id
    ).first_or_404()
    
    return render_template('payments/view.html', payment=payment)

@payments_bp.route('/<int:id>/edit')
@login_required
def edit(id):
    """Edit payment form"""
    payment = Payment.query.filter(
        Payment.id == id,
        Payment.organization_id == current_user.organization_id
    ).first_or_404()
    
    # Get customers
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True
    ).order_by(Customer.display_name).all()
    
    # Get deposit accounts
    deposit_accounts = Account.query.filter(
        Account.organization_id == current_user.organization_id,
        Account.type == AccountType.ASSET,
        Account.is_active == True
    ).order_by(Account.name).all()
    
    return render_template('payments/edit.html',
                         payment=payment,
                         customers=customers,
                         deposit_accounts=deposit_accounts,
                         PaymentMethod=PaymentMethod)

@payments_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete payment"""
    payment = Payment.query.filter(
        Payment.id == id,
        Payment.organization_id == current_user.organization_id
    ).first_or_404()
    
    try:
        # Reverse invoice allocations
        for allocation in payment.payment_allocations:
            invoice = allocation.invoice
            invoice.paid_amount = (invoice.paid_amount or 0) - allocation.allocated_amount
            invoice.balance = invoice.total - invoice.paid_amount
            
            # Update invoice status
            if invoice.balance >= invoice.total:
                invoice.status = InvoiceStatus.SENT
            elif invoice.paid_amount > 0:
                invoice.status = InvoiceStatus.PARTIAL
        
        # Delete allocations
        PaymentAllocation.query.filter_by(payment_id=payment.id).delete()
        
        # Delete journal entries
        JournalEntry.query.filter(
            JournalEntry.organization_id == current_user.organization_id,
            JournalEntry.reference == f"Payment {payment.payment_number}"
        ).delete()
        
        # Delete payment
        db.session.delete(payment)
        db.session.commit()
        
        flash(f'Payment {payment.payment_number} deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting payment: {str(e)}', 'error')
    
    return redirect(url_for('payments.index'))

def create_payment_journal_entry(payment, allocated_amount):
    """Create journal entry for payment"""
    try:
        # Get accounts receivable account
        ar_account = Account.query.filter(
            Account.organization_id == current_user.organization_id,
            Account.type == AccountType.ASSET,
            or_(
                Account.name.ilike('%receivable%'),
                Account.name.ilike('%a/r%'),
                Account.code.ilike('1200')
            )
        ).first()
        
        if not ar_account:
            # Create default AR account if it doesn't exist
            ar_account = Account(
                code='1200',
                name='Accounts Receivable',
                type=AccountType.ASSET,
                organization_id=current_user.organization_id
            )
            db.session.add(ar_account)
            db.session.flush()
        
        # Create journal entry
        journal_entry = JournalEntry(
            date=payment.payment_date,
            reference=f"Payment {payment.payment_number}",
            description=f"Customer payment from {payment.customer.display_name}",
            organization_id=current_user.organization_id,
            created_by=current_user.id
        )
        
        db.session.add(journal_entry)
        db.session.flush()
        
        # Debit: Deposit Account (increase cash/bank)
        debit_line = JournalLineItem(
            journal_entry_id=journal_entry.id,
            account_id=payment.deposit_account_id,
            description=f"Payment received from {payment.customer.display_name}",
            debit=payment.amount,
            credit=0,
            contact_type='customer',
            contact_id=payment.customer_id
        )
        db.session.add(debit_line)
        
        # Credit: Accounts Receivable (decrease what customer owes)
        credit_line = JournalLineItem(
            journal_entry_id=journal_entry.id,
            account_id=ar_account.id,
            description=f"Payment received from {payment.customer.display_name}",
            debit=0,
            credit=allocated_amount,
            contact_type='customer',
            contact_id=payment.customer_id
        )
        db.session.add(credit_line)
        
        # If there's unallocated amount (overpayment), credit to customer deposits/prepayments
        unallocated = payment.amount - allocated_amount
        if unallocated > 0:
            # Get or create customer deposits account
            deposits_account = Account.query.filter(
                Account.organization_id == current_user.organization_id,
                Account.type == AccountType.LIABILITY,
                Account.name.ilike('%deposit%')
            ).first()
            
            if not deposits_account:
                deposits_account = Account(
                    code='2300',
                    name='Customer Deposits',
                    type=AccountType.LIABILITY,
                    organization_id=current_user.organization_id
                )
                db.session.add(deposits_account)
                db.session.flush()
            
            unallocated_line = JournalLineItem(
                journal_entry_id=journal_entry.id,
                account_id=deposits_account.id,
                description=f"Unallocated payment from {payment.customer.display_name}",
                debit=0,
                credit=unallocated,
                contact_type='customer',
                contact_id=payment.customer_id
            )
            db.session.add(unallocated_line)
        
    except Exception as e:
        # Log the error but don't fail the payment creation
        print(f"Error creating journal entry for payment {payment.payment_number}: {str(e)}")
