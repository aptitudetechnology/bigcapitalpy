"""
Organizations API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from packages.server.src.models import Organization
from packages.server.src.database import db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request, serialize_model
)

organizations_api_bp = Blueprint('organizations_api', __name__)

@organizations_api_bp.route('/current', methods=['GET'])
@require_api_key
def get_current_organization():
    """Get current user's organization"""
    if not current_user.organization:
        return api_error('No organization found', 404)
    
    org_data = serialize_model(current_user.organization)
    
    return api_response(data={'organization': org_data})

@organizations_api_bp.route('/current', methods=['PUT'])
@require_api_key
@validate_json_request(['name'])
def update_current_organization():
    """Update current user's organization"""
    if not current_user.organization:
        return api_error('No organization found', 404)
    
    # Check if user has admin rights
    if current_user.role != 'admin':
        return api_error('Admin access required', 403)
    
    data = request.get_json()
    org = current_user.organization
    
    try:
        # Update organization fields
        org.name = data['name']
        org.legal_name = data.get('legal_name')
        org.tax_number = data.get('tax_number')
        org.registration_number = data.get('registration_number')
        org.industry = data.get('industry')
        org.phone = data.get('phone')
        org.email = data.get('email')
        org.website = data.get('website')
        org.address = data.get('address')
        org.city = data.get('city')
        org.state = data.get('state')
        org.postal_code = data.get('postal_code')
        org.country = data.get('country')
        org.currency = data.get('currency', org.currency)
        org.fiscal_year_start = data.get('fiscal_year_start', org.fiscal_year_start)
        org.timezone = data.get('timezone', org.timezone)
        org.logo_url = data.get('logo_url')
        
        db.session.commit()
        
        org_data = serialize_model(org)
        
        return api_response(
            data={'organization': org_data},
            message='Organization updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update organization: {str(e)}', 500)

@organizations_api_bp.route('/settings', methods=['GET'])
@require_api_key
def get_organization_settings():
    """Get organization settings for current user"""
    if not current_user.organization:
        return api_error('No organization found', 404)
    
    org = current_user.organization
    
    settings = {
        'currency': org.currency,
        'fiscal_year_start': org.fiscal_year_start,
        'timezone': org.timezone,
        'date_format': 'YYYY-MM-DD',  # Default format
        'number_format': 'en-US',     # Default format
        'invoice_prefix': 'INV-',
        'auto_invoice_numbering': True
    }
    
    return api_response(data={'settings': settings})

@organizations_api_bp.route('/stats', methods=['GET'])
@require_api_key
def get_organization_stats():
    """Get organization statistics"""
    if not current_user.organization:
        return api_error('No organization found', 404)
    
    org_id = current_user.organization_id
    
    # Count various entities
    from packages.server.src.models import Customer, Vendor, Item, Invoice, Account
    
    stats = {
        'customers': Customer.query.filter_by(
            organization_id=org_id, is_active=True
        ).count(),
        'vendors': Vendor.query.filter_by(
            organization_id=org_id, is_active=True
        ).count(),
        'items': Item.query.filter_by(
            organization_id=org_id, is_active=True
        ).count(),
        'invoices': Invoice.query.filter_by(
            organization_id=org_id
        ).count(),
        'accounts': Account.query.filter_by(
            organization_id=org_id, is_active=True
        ).count(),
        'users': len(current_user.organization.users)
    }
    
    return api_response(data={'stats': stats})
