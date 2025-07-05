"""
Payments API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime
from decimal import Decimal
from packages.server.src.models import Payment, PaymentAllocation, PaymentMethod, Customer, Invoice, Account
from packages.server.src.database import db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request,
    paginate_query, get_pagination_params, serialize_model
)

payments_api_bp = Blueprint('payments_api', __name__)

@payments_api_bp.route('', methods=['GET'])
@require_api_key
def list_payments():
    """Get paginated list of payments"""
    page, per_page = get_pagination_params()
    
    # Build query
    query = Payment.query.filter_by(
        organization_id=current_user.organization_id
    )
    
    # Apply customer filter
    customer_id = request.args.get('customer_id', type=int)
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    
    # Apply payment method filter
    method = request.args.get('method', '').strip()
    if method:
        try:
            method_enum = PaymentMethod(method)
            query = query.filter(Payment.payment_method == method_enum)
        except ValueError:
            pass
    
    # Apply date range filter
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Payment.payment_date >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Payment.payment_date <= end_date)
        except ValueError:
            pass
    
    # Apply search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.join(Customer).filter(
            Payment.payment_number.ilike(f'%{search}%') |
            Payment.reference.ilike(f'%{search}%') |
            Customer.display_name.ilike(f'%{search}%')
        )
    
    # Apply sorting
    sort_by = request.args.get('sort_by', 'payment_date')
    sort_order = request.args.get('sort_order', 'desc')
    
    if hasattr(Payment, sort_by):
        column = getattr(Payment, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    
    # Paginate results
    result = paginate_query(query, page, per_page)
    
    # Serialize payments with customer information
    payments_data = []
    for payment in result['items']:
        payment_data = serialize_model(payment)
        payment_data['customer'] = {
            'id': payment.customer.id,
            'display_name': payment.customer.display_name,
            'email': payment.customer.email
        }
        payment_data['deposit_account'] = {
            'id': payment.deposit_account.id,
            'name': payment.deposit_account.name,
            'code': payment.deposit_account.code
        }
        payments_data.append(payment_data)
    
    return api_response(data={
        'payments': payments_data,
        'pagination': result['pagination']
    })

@payments_api_bp.route('/<int:payment_id>', methods=['GET'])
@require_api_key
def get_payment(payment_id):
    """Get specific payment by ID with allocations"""
    payment = Payment.query.filter_by(
        id=payment_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not payment:
        return api_error('Payment not found', 404)
    
    payment_data = serialize_model(payment)
    payment_data['customer'] = serialize_model(payment.customer)
    payment_data['deposit_account'] = serialize_model(payment.deposit_account)
    
    # Add allocations
    allocations_data = []
    for allocation in payment.payment_allocations:
        allocation_data = serialize_model(allocation)
        allocation_data['invoice'] = {
            'id': allocation.invoice.id,
            'invoice_number': allocation.invoice.invoice_number,
            'invoice_date': allocation.invoice.invoice_date.isoformat(),
            'total': float(allocation.invoice.total),
            'balance': float(allocation.invoice.balance)
        }
        allocations_data.append(allocation_data)
    
    payment_data['allocations'] = allocations_data
    
    return api_response(data={'payment': payment_data})

@payments_api_bp.route('', methods=['POST'])
@require_api_key
@validate_json_request(['customer_id', 'payment_date', 'amount', 'payment_method', 'deposit_account_id'])
def create_payment():
    """Create new payment"""
    data = request.get_json()
    
    # Validate customer exists
    customer = Customer.query.filter_by(
        id=data['customer_id'],
        organization_id=current_user.organization_id
    ).first()
    
    if not customer:
        return api_error('Customer not found', 404)
    
    # Validate deposit account exists
    deposit_account = Account.query.filter_by(
        id=data['deposit_account_id'],
        organization_id=current_user.organization_id
    ).first()
    
    if not deposit_account:
        return api_error('Deposit account not found', 404)
    
    try:
        # Generate payment number
        last_payment = Payment.query.filter_by(
            organization_id=current_user.organization_id
        ).order_by(Payment.id.desc()).first()
        
        if last_payment:
            last_number = int(last_payment.payment_number.split('-')[-1])
            payment_number = f"PMT-{last_number + 1:05d}"
        else:
            payment_number = "PMT-00001"
        
        # Parse date and validate payment method
        payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
        payment_method = PaymentMethod(data['payment_method'])
        amount = Decimal(str(data['amount']))
        
        if amount <= 0:
            return api_error('Payment amount must be greater than zero', 400)
        
        # Create payment
        payment = Payment(
            payment_number=payment_number,
            payment_date=payment_date,
            amount=amount,
            payment_method=payment_method,
            reference=data.get('reference'),
            notes=data.get('notes'),
            bank_name=data.get('bank_name'),
            check_number=data.get('check_number'),
            customer_id=data['customer_id'],
            deposit_account_id=data['deposit_account_id'],
            organization_id=current_user.organization_id,
            created_by=current_user.id
        )
        
        db.session.add(payment)
        db.session.flush()  # Get payment ID
        
        # Handle allocations if provided
        allocations_data = data.get('allocations', [])
        total_allocated = Decimal('0.00')
        
        for allocation_data in allocations_data:
            invoice_id = allocation_data.get('invoice_id')
            allocated_amount = Decimal(str(allocation_data.get('amount', 0)))
            
            if allocated_amount > 0 and invoice_id:
                # Validate invoice exists and belongs to customer
                invoice = Invoice.query.filter_by(
                    id=invoice_id,
                    customer_id=data['customer_id'],
                    organization_id=current_user.organization_id
                ).first()
                
                if invoice and allocated_amount <= invoice.balance:
                    allocation = PaymentAllocation(
                        payment_id=payment.id,
                        invoice_id=invoice_id,
                        allocated_amount=allocated_amount
                    )
                    db.session.add(allocation)
                    
                    # Update invoice
                    invoice.paid_amount = (invoice.paid_amount or 0) + allocated_amount
                    invoice.balance = invoice.total - invoice.paid_amount
                    
                    # Update invoice status
                    if invoice.balance <= 0:
                        invoice.status = InvoiceStatus.PAID
                    elif invoice.paid_amount > 0:
                        invoice.status = InvoiceStatus.PARTIAL
                    
                    total_allocated += allocated_amount
        
        db.session.commit()
        
        # Return created payment
        payment_data = serialize_model(payment)
        payment_data['customer'] = serialize_model(customer)
        payment_data['deposit_account'] = serialize_model(deposit_account)
        
        return api_response(
            data={'payment': payment_data},
            message='Payment created successfully',
            status_code=201
        )
        
    except ValueError as e:
        db.session.rollback()
        return api_error(f'Invalid data: {str(e)}', 400)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to create payment: {str(e)}', 500)

@payments_api_bp.route('/<int:payment_id>', methods=['PUT'])
@require_api_key
@validate_json_request(['customer_id', 'payment_date', 'amount', 'payment_method', 'deposit_account_id'])
def update_payment(payment_id):
    """Update existing payment"""
    payment = Payment.query.filter_by(
        id=payment_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not payment:
        return api_error('Payment not found', 404)
    
    data = request.get_json()
    
    try:
        # Reverse existing allocations
        for allocation in payment.payment_allocations:
            invoice = allocation.invoice
            invoice.paid_amount = (invoice.paid_amount or 0) - allocation.allocated_amount
            invoice.balance = invoice.total - invoice.paid_amount
            
            # Update invoice status
            if invoice.balance >= invoice.total:
                invoice.status = InvoiceStatus.SENT
            elif invoice.paid_amount > 0:
                invoice.status = InvoiceStatus.PARTIAL
        
        # Delete existing allocations
        PaymentAllocation.query.filter_by(payment_id=payment.id).delete()
        
        # Update payment fields
        payment.payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
        payment.amount = Decimal(str(data['amount']))
        payment.payment_method = PaymentMethod(data['payment_method'])
        payment.customer_id = data['customer_id']
        payment.deposit_account_id = data['deposit_account_id']
        payment.reference = data.get('reference')
        payment.notes = data.get('notes')
        payment.bank_name = data.get('bank_name')
        payment.check_number = data.get('check_number')
        
        # Re-apply allocations
        allocations_data = data.get('allocations', [])
        for allocation_data in allocations_data:
            invoice_id = allocation_data.get('invoice_id')
            allocated_amount = Decimal(str(allocation_data.get('amount', 0)))
            
            if allocated_amount > 0 and invoice_id:
                invoice = Invoice.query.filter_by(
                    id=invoice_id,
                    customer_id=data['customer_id'],
                    organization_id=current_user.organization_id
                ).first()
                
                if invoice:
                    allocation = PaymentAllocation(
                        payment_id=payment.id,
                        invoice_id=invoice_id,
                        allocated_amount=allocated_amount
                    )
                    db.session.add(allocation)
                    
                    # Update invoice
                    invoice.paid_amount = (invoice.paid_amount or 0) + allocated_amount
                    invoice.balance = invoice.total - invoice.paid_amount
                    
                    # Update invoice status
                    if invoice.balance <= 0:
                        invoice.status = InvoiceStatus.PAID
                    elif invoice.paid_amount > 0:
                        invoice.status = InvoiceStatus.PARTIAL
        
        db.session.commit()
        
        payment_data = serialize_model(payment)
        
        return api_response(
            data={'payment': payment_data},
            message='Payment updated successfully'
        )
        
    except ValueError as e:
        db.session.rollback()
        return api_error(f'Invalid data: {str(e)}', 400)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update payment: {str(e)}', 500)

@payments_api_bp.route('/<int:payment_id>', methods=['DELETE'])
@require_api_key
def delete_payment(payment_id):
    """Delete payment"""
    payment = Payment.query.filter_by(
        id=payment_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not payment:
        return api_error('Payment not found', 404)
    
    try:
        # Reverse allocations
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
        
        # Delete payment
        db.session.delete(payment)
        db.session.commit()
        
        return api_response(message='Payment deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to delete payment: {str(e)}', 500)

@payments_api_bp.route('/stats', methods=['GET'])
@require_api_key
def get_payment_stats():
    """Get payment statistics"""
    from sqlalchemy import func
    
    stats = {}
    
    # Total payments
    total_payments = db.session.query(
        func.sum(Payment.amount)
    ).filter_by(organization_id=current_user.organization_id).scalar() or 0
    
    # Payments this month
    payments_this_month = db.session.query(
        func.sum(Payment.amount)
    ).filter(
        Payment.organization_id == current_user.organization_id,
        Payment.payment_date >= date.today().replace(day=1)
    ).scalar() or 0
    
    # Payment count
    payment_count = Payment.query.filter_by(
        organization_id=current_user.organization_id
    ).count()
    
    # Count by method
    method_counts = db.session.query(
        Payment.payment_method,
        func.count(Payment.id),
        func.sum(Payment.amount)
    ).filter_by(
        organization_id=current_user.organization_id
    ).group_by(Payment.payment_method).all()
    
    method_stats = {}
    for method, count, amount in method_counts:
        method_stats[method.value] = {
            'count': count,
            'amount': float(amount or 0)
        }
    
    stats.update({
        'total_payments': float(total_payments),
        'payments_this_month': float(payments_this_month),
        'payment_count': payment_count,
        'by_method': method_stats
    })
    
    return api_response(data={'stats': stats})

@payments_api_bp.route('/customer/<int:customer_id>/outstanding-invoices', methods=['GET'])
@require_api_key
def get_customer_outstanding_invoices(customer_id):
    """Get outstanding invoices for a customer"""
    from packages.server.src.models import InvoiceStatus
    
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
            'invoice_date': invoice.invoice_date.isoformat(),
            'due_date': invoice.due_date.isoformat(),
            'total': float(invoice.total),
            'paid_amount': float(invoice.paid_amount or 0),
            'balance': float(invoice.balance),
            'status': invoice.status.value
        })
    
    return api_response(data={'invoices': invoice_data})
