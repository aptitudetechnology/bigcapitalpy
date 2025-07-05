"""
Invoices API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime
from decimal import Decimal
from packages.server.src.models import Invoice, InvoiceLineItem, Customer, Item, InvoiceStatus
from packages.server.src.database import db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request,
    paginate_query, get_pagination_params, serialize_model
)

invoices_api_bp = Blueprint('invoices_api', __name__)

@invoices_api_bp.route('', methods=['GET'])
@require_api_key
def list_invoices():
    """Get paginated list of invoices"""
    page, per_page = get_pagination_params()
    
    # Build query
    query = Invoice.query.filter_by(
        organization_id=current_user.organization_id
    )
    
    # Apply status filter
    status = request.args.get('status', '').strip()
    if status:
        try:
            status_enum = InvoiceStatus(status)
            query = query.filter(Invoice.status == status_enum)
        except ValueError:
            pass
    
    # Apply customer filter
    customer_id = request.args.get('customer_id', type=int)
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    
    # Apply date range filter
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date <= end_date)
        except ValueError:
            pass
    
    # Apply search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.join(Customer).filter(
            Invoice.invoice_number.ilike(f'%{search}%') |
            Invoice.reference.ilike(f'%{search}%') |
            Customer.display_name.ilike(f'%{search}%')
        )
    
    # Apply sorting
    sort_by = request.args.get('sort_by', 'invoice_date')
    sort_order = request.args.get('sort_order', 'desc')
    
    if hasattr(Invoice, sort_by):
        column = getattr(Invoice, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    
    # Paginate results
    result = paginate_query(query, page, per_page)
    
    # Serialize invoices with customer information
    invoices_data = []
    for invoice in result['items']:
        invoice_data = serialize_model(invoice)
        invoice_data['customer'] = {
            'id': invoice.customer.id,
            'display_name': invoice.customer.display_name,
            'email': invoice.customer.email
        }
        invoices_data.append(invoice_data)
    
    return api_response(data={
        'invoices': invoices_data,
        'pagination': result['pagination']
    })

@invoices_api_bp.route('/<int:invoice_id>', methods=['GET'])
@require_api_key
def get_invoice(invoice_id):
    """Get specific invoice by ID with line items"""
    invoice = Invoice.query.filter_by(
        id=invoice_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not invoice:
        return api_error('Invoice not found', 404)
    
    invoice_data = serialize_model(invoice)
    invoice_data['customer'] = serialize_model(invoice.customer)
    
    # Add line items
    line_items_data = []
    for line_item in invoice.line_items:
        line_data = serialize_model(line_item)
        if line_item.item:
            line_data['item'] = {
                'id': line_item.item.id,
                'name': line_item.item.name,
                'sku': line_item.item.sku
            }
        line_items_data.append(line_data)
    
    invoice_data['line_items'] = line_items_data
    
    return api_response(data={'invoice': invoice_data})

@invoices_api_bp.route('', methods=['POST'])
@require_api_key
@validate_json_request(['customer_id', 'invoice_date', 'due_date', 'line_items'])
def create_invoice():
    """Create new invoice with line items"""
    data = request.get_json()
    
    # Validate customer exists
    customer = Customer.query.filter_by(
        id=data['customer_id'],
        organization_id=current_user.organization_id
    ).first()
    
    if not customer:
        return api_error('Customer not found', 404)
    
    # Validate line items
    line_items_data = data.get('line_items', [])
    if not line_items_data:
        return api_error('At least one line item is required', 400)
    
    try:
        # Generate invoice number
        last_invoice = Invoice.query.filter_by(
            organization_id=current_user.organization_id
        ).order_by(Invoice.id.desc()).first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            invoice_number = f"INV-{last_number + 1:05d}"
        else:
            invoice_number = "INV-00001"
        
        # Parse dates
        invoice_date = datetime.strptime(data['invoice_date'], '%Y-%m-%d').date()
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            reference=data.get('reference'),
            invoice_date=invoice_date,
            due_date=due_date,
            customer_id=data['customer_id'],
            currency=data.get('currency', 'USD'),
            terms=data.get('terms'),
            notes=data.get('notes'),
            organization_id=current_user.organization_id
        )
        
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID
        
        # Create line items and calculate totals
        subtotal = Decimal('0.00')
        tax_amount = Decimal('0.00')
        
        for line_data in line_items_data:
            if not line_data.get('description'):
                raise ValueError('Line item description is required')
            
            quantity = Decimal(str(line_data.get('quantity', 1)))
            rate = Decimal(str(line_data.get('rate', 0)))
            tax_rate = Decimal(str(line_data.get('tax_rate', 0)))
            
            line_amount = quantity * rate
            line_tax = line_amount * (tax_rate / 100)
            
            line_item = InvoiceLineItem(
                invoice_id=invoice.id,
                item_id=line_data.get('item_id'),
                description=line_data['description'],
                quantity=quantity,
                rate=rate,
                amount=line_amount,
                tax_rate=tax_rate,
                tax_amount=line_tax
            )
            
            db.session.add(line_item)
            subtotal += line_amount
            tax_amount += line_tax
        
        # Update invoice totals
        discount_amount = Decimal(str(data.get('discount_amount', 0)))
        invoice.subtotal = subtotal
        invoice.discount_amount = discount_amount
        invoice.tax_amount = tax_amount
        invoice.total = subtotal - discount_amount + tax_amount
        invoice.balance = invoice.total
        
        db.session.commit()
        
        # Return created invoice
        invoice_data = serialize_model(invoice)
        invoice_data['customer'] = serialize_model(customer)
        
        return api_response(
            data={'invoice': invoice_data},
            message='Invoice created successfully',
            status_code=201
        )
        
    except ValueError as e:
        db.session.rollback()
        return api_error(f'Invalid data: {str(e)}', 400)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to create invoice: {str(e)}', 500)

@invoices_api_bp.route('/<int:invoice_id>', methods=['PUT'])
@require_api_key
@validate_json_request(['customer_id', 'invoice_date', 'due_date'])
def update_invoice(invoice_id):
    """Update existing invoice"""
    invoice = Invoice.query.filter_by(
        id=invoice_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not invoice:
        return api_error('Invoice not found', 404)
    
    # Check if invoice can be modified
    if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
        return api_error('Cannot modify paid or cancelled invoices', 400)
    
    data = request.get_json()
    
    try:
        # Update invoice fields
        invoice.reference = data.get('reference')
        invoice.invoice_date = datetime.strptime(data['invoice_date'], '%Y-%m-%d').date()
        invoice.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        invoice.customer_id = data['customer_id']
        invoice.currency = data.get('currency', invoice.currency)
        invoice.terms = data.get('terms')
        invoice.notes = data.get('notes')
        
        # Update line items if provided
        if 'line_items' in data:
            # Remove existing line items
            InvoiceLineItem.query.filter_by(invoice_id=invoice.id).delete()
            
            # Add new line items
            subtotal = Decimal('0.00')
            tax_amount = Decimal('0.00')
            
            for line_data in data['line_items']:
                quantity = Decimal(str(line_data.get('quantity', 1)))
                rate = Decimal(str(line_data.get('rate', 0)))
                tax_rate = Decimal(str(line_data.get('tax_rate', 0)))
                
                line_amount = quantity * rate
                line_tax = line_amount * (tax_rate / 100)
                
                line_item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    item_id=line_data.get('item_id'),
                    description=line_data['description'],
                    quantity=quantity,
                    rate=rate,
                    amount=line_amount,
                    tax_rate=tax_rate,
                    tax_amount=line_tax
                )
                
                db.session.add(line_item)
                subtotal += line_amount
                tax_amount += line_tax
            
            # Update totals
            discount_amount = Decimal(str(data.get('discount_amount', 0)))
            invoice.subtotal = subtotal
            invoice.discount_amount = discount_amount
            invoice.tax_amount = tax_amount
            invoice.total = subtotal - discount_amount + tax_amount
            invoice.balance = invoice.total - invoice.paid_amount
        
        db.session.commit()
        
        invoice_data = serialize_model(invoice)
        
        return api_response(
            data={'invoice': invoice_data},
            message='Invoice updated successfully'
        )
        
    except ValueError as e:
        db.session.rollback()
        return api_error(f'Invalid data: {str(e)}', 400)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update invoice: {str(e)}', 500)

@invoices_api_bp.route('/<int:invoice_id>', methods=['DELETE'])
@require_api_key
def delete_invoice(invoice_id):
    """Delete invoice (only if draft)"""
    invoice = Invoice.query.filter_by(
        id=invoice_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not invoice:
        return api_error('Invoice not found', 404)
    
    if invoice.status != InvoiceStatus.DRAFT:
        return api_error('Only draft invoices can be deleted', 400)
    
    try:
        # Delete line items first
        InvoiceLineItem.query.filter_by(invoice_id=invoice.id).delete()
        
        # Delete invoice
        db.session.delete(invoice)
        db.session.commit()
        
        return api_response(message='Invoice deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to delete invoice: {str(e)}', 500)

@invoices_api_bp.route('/<int:invoice_id>/status', methods=['PUT'])
@require_api_key
@validate_json_request(['status'])
def update_invoice_status(invoice_id):
    """Update invoice status"""
    invoice = Invoice.query.filter_by(
        id=invoice_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not invoice:
        return api_error('Invoice not found', 404)
    
    data = request.get_json()
    
    try:
        new_status = InvoiceStatus(data['status'])
        invoice.status = new_status
        
        db.session.commit()
        
        return api_response(
            data={'status': new_status.value},
            message=f'Invoice status updated to {new_status.value}'
        )
        
    except ValueError:
        return api_error('Invalid status', 400)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update status: {str(e)}', 500)

@invoices_api_bp.route('/stats', methods=['GET'])
@require_api_key
def get_invoice_stats():
    """Get invoice statistics"""
    stats = {}
    
    # Count by status
    for status in InvoiceStatus:
        count = Invoice.query.filter_by(
            organization_id=current_user.organization_id,
            status=status
        ).count()
        stats[f'{status.value}_count'] = count
    
    # Total amounts
    totals = db.session.query(
        db.func.sum(Invoice.total).label('total_invoiced'),
        db.func.sum(Invoice.paid_amount).label('total_paid'),
        db.func.sum(Invoice.balance).label('total_outstanding')
    ).filter_by(organization_id=current_user.organization_id).first()
    
    stats.update({
        'total_invoiced': float(totals.total_invoiced or 0),
        'total_paid': float(totals.total_paid or 0),
        'total_outstanding': float(totals.total_outstanding or 0)
    })
    
    return api_response(data={'stats': stats})
