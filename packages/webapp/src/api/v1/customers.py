"""
Customers API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from packages.server.src.models import Customer
from packages.server.src.database import db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request,
    paginate_query, get_pagination_params, serialize_model
)

customers_api_bp = Blueprint('customers_api', __name__)

@customers_api_bp.route('', methods=['GET'])
@require_api_key
def list_customers():
    """Get paginated list of customers"""
    page, per_page = get_pagination_params()
    
    # Build query
    query = Customer.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    )
    
    # Apply search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            Customer.display_name.ilike(f'%{search}%') |
            Customer.email.ilike(f'%{search}%') |
            Customer.company_name.ilike(f'%{search}%')
        )
    
    # Apply sorting
    sort_by = request.args.get('sort_by', 'display_name')
    sort_order = request.args.get('sort_order', 'asc')
    
    if hasattr(Customer, sort_by):
        column = getattr(Customer, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    
    # Paginate results
    result = paginate_query(query, page, per_page)
    
    # Serialize customers
    customers_data = [serialize_model(customer) for customer in result['items']]
    
    return api_response(data={
        'customers': customers_data,
        'pagination': result['pagination']
    })

@customers_api_bp.route('/<int:customer_id>', methods=['GET'])
@require_api_key
def get_customer(customer_id):
    """Get specific customer by ID"""
    customer = Customer.query.filter_by(
        id=customer_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not customer:
        return api_error('Customer not found', 404)
    
    customer_data = serialize_model(customer)
    
    return api_response(data={'customer': customer_data})

@customers_api_bp.route('', methods=['POST'])
@require_api_key
@validate_json_request(['display_name'])
def create_customer():
    """Create new customer"""
    data = request.get_json()
    
    try:
        customer = Customer(
            display_name=data['display_name'],
            company_name=data.get('company_name'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            website=data.get('website'),
            billing_address=data.get('billing_address'),
            billing_city=data.get('billing_city'),
            billing_state=data.get('billing_state'),
            billing_postal_code=data.get('billing_postal_code'),
            billing_country=data.get('billing_country'),
            shipping_address=data.get('shipping_address'),
            shipping_city=data.get('shipping_city'),
            shipping_state=data.get('shipping_state'),
            shipping_postal_code=data.get('shipping_postal_code'),
            shipping_country=data.get('shipping_country'),
            currency=data.get('currency', 'USD'),
            opening_balance=data.get('opening_balance', 0),
            credit_limit=data.get('credit_limit', 0),
            tax_number=data.get('tax_number'),
            notes=data.get('notes'),
            organization_id=current_user.organization_id
        )
        
        db.session.add(customer)
        db.session.commit()
        
        customer_data = serialize_model(customer)
        
        return api_response(
            data={'customer': customer_data},
            message='Customer created successfully',
            status_code=201
        )
        
    except IntegrityError:
        db.session.rollback()
        return api_error('A customer with this information already exists', 409)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to create customer: {str(e)}', 500)

@customers_api_bp.route('/<int:customer_id>', methods=['PUT'])
@require_api_key
@validate_json_request(['display_name'])
def update_customer(customer_id):
    """Update existing customer"""
    customer = Customer.query.filter_by(
        id=customer_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not customer:
        return api_error('Customer not found', 404)
    
    data = request.get_json()
    
    try:
        # Update fields
        customer.display_name = data['display_name']
        customer.company_name = data.get('company_name')
        customer.first_name = data.get('first_name')
        customer.last_name = data.get('last_name')
        customer.email = data.get('email')
        customer.phone = data.get('phone')
        customer.website = data.get('website')
        customer.billing_address = data.get('billing_address')
        customer.billing_city = data.get('billing_city')
        customer.billing_state = data.get('billing_state')
        customer.billing_postal_code = data.get('billing_postal_code')
        customer.billing_country = data.get('billing_country')
        customer.shipping_address = data.get('shipping_address')
        customer.shipping_city = data.get('shipping_city')
        customer.shipping_state = data.get('shipping_state')
        customer.shipping_postal_code = data.get('shipping_postal_code')
        customer.shipping_country = data.get('shipping_country')
        customer.currency = data.get('currency', customer.currency)
        customer.opening_balance = data.get('opening_balance', customer.opening_balance)
        customer.credit_limit = data.get('credit_limit', customer.credit_limit)
        customer.tax_number = data.get('tax_number')
        customer.notes = data.get('notes')
        
        db.session.commit()
        
        customer_data = serialize_model(customer)
        
        return api_response(
            data={'customer': customer_data},
            message='Customer updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update customer: {str(e)}', 500)

@customers_api_bp.route('/<int:customer_id>', methods=['DELETE'])
@require_api_key
def delete_customer(customer_id):
    """Soft delete customer"""
    customer = Customer.query.filter_by(
        id=customer_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not customer:
        return api_error('Customer not found', 404)
    
    try:
        # Soft delete
        customer.is_active = False
        db.session.commit()
        
        return api_response(message='Customer deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to delete customer: {str(e)}', 500)

@customers_api_bp.route('/search', methods=['GET'])
@require_api_key
def search_customers():
    """Search customers by name or email"""
    query_str = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 10)), 50)
    
    if not query_str:
        return api_response(data={'customers': []})
    
    customers = Customer.query.filter(
        Customer.organization_id == current_user.organization_id,
        Customer.is_active == True,
        (Customer.display_name.ilike(f'%{query_str}%') |
         Customer.email.ilike(f'%{query_str}%') |
         Customer.company_name.ilike(f'%{query_str}%'))
    ).limit(limit).all()
    
    customers_data = [
        {
            'id': customer.id,
            'display_name': customer.display_name,
            'email': customer.email,
            'company_name': customer.company_name
        }
        for customer in customers
    ]
    
    return api_response(data={'customers': customers_data})
