"""
Vendors API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from packages.server.src.models import Vendor
from packages.server.src.database import db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request,
    paginate_query, get_pagination_params, serialize_model
)

vendors_api_bp = Blueprint('vendors_api', __name__)

@vendors_api_bp.route('', methods=['GET'])
@require_api_key
def list_vendors():
    """Get paginated list of vendors"""
    page, per_page = get_pagination_params()
    
    # Build query
    query = Vendor.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    )
    
    # Apply search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            Vendor.display_name.ilike(f'%{search}%') |
            Vendor.email.ilike(f'%{search}%') |
            Vendor.company_name.ilike(f'%{search}%')
        )
    
    # Apply sorting
    sort_by = request.args.get('sort_by', 'display_name')
    sort_order = request.args.get('sort_order', 'asc')
    
    if hasattr(Vendor, sort_by):
        column = getattr(Vendor, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    
    # Paginate results
    result = paginate_query(query, page, per_page)
    
    # Serialize vendors
    vendors_data = [serialize_model(vendor) for vendor in result['items']]
    
    return api_response(data={
        'vendors': vendors_data,
        'pagination': result['pagination']
    })

@vendors_api_bp.route('/<int:vendor_id>', methods=['GET'])
@require_api_key
def get_vendor(vendor_id):
    """Get specific vendor by ID"""
    vendor = Vendor.query.filter_by(
        id=vendor_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not vendor:
        return api_error('Vendor not found', 404)
    
    vendor_data = serialize_model(vendor)
    
    return api_response(data={'vendor': vendor_data})

@vendors_api_bp.route('', methods=['POST'])
@require_api_key
@validate_json_request(['display_name'])
def create_vendor():
    """Create new vendor"""
    data = request.get_json()
    
    try:
        vendor = Vendor(
            display_name=data['display_name'],
            company_name=data.get('company_name'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            website=data.get('website'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            currency=data.get('currency', 'USD'),
            opening_balance=data.get('opening_balance', 0),
            tax_number=data.get('tax_number'),
            notes=data.get('notes'),
            organization_id=current_user.organization_id
        )
        
        db.session.add(vendor)
        db.session.commit()
        
        vendor_data = serialize_model(vendor)
        
        return api_response(
            data={'vendor': vendor_data},
            message='Vendor created successfully',
            status_code=201
        )
        
    except IntegrityError:
        db.session.rollback()
        return api_error('A vendor with this information already exists', 409)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to create vendor: {str(e)}', 500)

@vendors_api_bp.route('/<int:vendor_id>', methods=['PUT'])
@require_api_key
@validate_json_request(['display_name'])
def update_vendor(vendor_id):
    """Update existing vendor"""
    vendor = Vendor.query.filter_by(
        id=vendor_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not vendor:
        return api_error('Vendor not found', 404)
    
    data = request.get_json()
    
    try:
        # Update fields
        vendor.display_name = data['display_name']
        vendor.company_name = data.get('company_name')
        vendor.first_name = data.get('first_name')
        vendor.last_name = data.get('last_name')
        vendor.email = data.get('email')
        vendor.phone = data.get('phone')
        vendor.website = data.get('website')
        vendor.address = data.get('address')
        vendor.city = data.get('city')
        vendor.state = data.get('state')
        vendor.postal_code = data.get('postal_code')
        vendor.country = data.get('country')
        vendor.currency = data.get('currency', vendor.currency)
        vendor.opening_balance = data.get('opening_balance', vendor.opening_balance)
        vendor.tax_number = data.get('tax_number')
        vendor.notes = data.get('notes')
        
        db.session.commit()
        
        vendor_data = serialize_model(vendor)
        
        return api_response(
            data={'vendor': vendor_data},
            message='Vendor updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update vendor: {str(e)}', 500)

@vendors_api_bp.route('/<int:vendor_id>', methods=['DELETE'])
@require_api_key
def delete_vendor(vendor_id):
    """Soft delete vendor"""
    vendor = Vendor.query.filter_by(
        id=vendor_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not vendor:
        return api_error('Vendor not found', 404)
    
    try:
        # Soft delete
        vendor.is_active = False
        db.session.commit()
        
        return api_response(message='Vendor deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to delete vendor: {str(e)}', 500)

@vendors_api_bp.route('/search', methods=['GET'])
@require_api_key
def search_vendors():
    """Search vendors by name or email"""
    query_str = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 10)), 50)
    
    if not query_str:
        return api_response(data={'vendors': []})
    
    vendors = Vendor.query.filter(
        Vendor.organization_id == current_user.organization_id,
        Vendor.is_active == True,
        (Vendor.display_name.ilike(f'%{query_str}%') |
         Vendor.email.ilike(f'%{query_str}%') |
         Vendor.company_name.ilike(f'%{query_str}%'))
    ).limit(limit).all()
    
    vendors_data = [
        {
            'id': vendor.id,
            'display_name': vendor.display_name,
            'email': vendor.email,
            'company_name': vendor.company_name
        }
        for vendor in vendors
    ]
    
    return api_response(data={'vendors': vendors_data})
