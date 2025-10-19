"""
Tax API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from packages.server.src.models import TaxCode, TaxType, db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request,
    paginate_query, get_pagination_params, serialize_model
)

tax_api_bp = Blueprint('tax_api', __name__)

@tax_api_bp.route('', methods=['GET'])
@require_api_key
def list_taxes():
    """Get paginated list of taxes"""
    page, per_page = get_pagination_params()

    # Build query
    query = TaxCode.query.filter_by(organization_id=current_user.organization_id)

    # Apply filters
    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter(TaxCode.is_active == (is_active.lower() == 'true'))

    # Apply search
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            TaxCode.name.ilike(f'%{search}%') |
            TaxCode.description.ilike(f'%{search}%') |
            TaxCode.code.ilike(f'%{search}%')
        )

    # Apply sorting
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    if hasattr(TaxCode, sort_by):
        column = getattr(TaxCode, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # Paginate results
    result = paginate_query(query, page, per_page)

    # Serialize tax codes
    taxes_data = []
    for tax in result['items']:
        tax_data = serialize_model(tax)
        # expose simple fields
        tax_data['rate'] = float(tax.rate) if tax.rate is not None else None
        tax_data['tax_type'] = tax.tax_type.value if getattr(tax, 'tax_type', None) else None
        taxes_data.append(tax_data)

    return api_response(data={
        'taxes': taxes_data,
        'pagination': result['pagination']
    })

@tax_api_bp.route('/<int:tax_id>', methods=['GET'])
@require_api_key
def get_tax(tax_id):
    """Get specific tax with rates"""
    tax = TaxCode.query.filter_by(
        id=tax_id,
        organization_id=current_user.organization_id
    ).first()

    if not tax:
        return api_error('Tax not found', 404)

    tax_data = serialize_model(tax)
    tax_data['rate'] = float(tax.rate) if tax.rate is not None else None
    tax_data['tax_type'] = tax.tax_type.value if getattr(tax, 'tax_type', None) else None

    return api_response(data={'tax': tax_data})

@tax_api_bp.route('', methods=['POST'])
@require_api_key
@validate_json_request(['name', 'rate'])
def create_tax():
    """Create new tax code (single-rate)"""
    data = request.get_json()

    try:
        rate_value = Decimal(str(data.get('rate', 0)))
        if rate_value < 0 or rate_value > 100:
            return api_error('Tax rate must be between 0 and 100', 400)

        # Parse tax_type if provided
        tax_type_raw = data.get('tax_type') or data.get('type')
        tax_type = None
        if tax_type_raw:
            # Try to match by value or name
            try:
                tax_type = TaxType(tax_type_raw)
            except Exception:
                try:
                    tax_type = TaxType[tax_type_raw.upper()]
                except Exception:
                    return api_error('Invalid tax_type', 400)

        tax = TaxCode(
            code=data.get('code', ''),
            name=data['name'],
            description=data.get('description', ''),
            tax_type=tax_type or TaxType.GST_STANDARD,
            rate=rate_value,
            is_active=data.get('is_active', True),
            organization_id=current_user.organization_id
        )

        db.session.add(tax)
        db.session.commit()

        tax_data = serialize_model(tax)
        tax_data['rate'] = float(tax.rate) if tax.rate is not None else None
        tax_data['tax_type'] = tax.tax_type.value if getattr(tax, 'tax_type', None) else None

        return api_response(
            data={'tax': tax_data},
            message='Tax created successfully',
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to create tax: {str(e)}', 500)

@tax_api_bp.route('/<int:tax_id>', methods=['PUT'])
@require_api_key
@validate_json_request(['name', 'rate'])
def update_tax(tax_id):
    """Update existing tax code"""
    tax = TaxCode.query.filter_by(
        id=tax_id,
        organization_id=current_user.organization_id
    ).first()

    if not tax:
        return api_error('Tax not found', 404)

    data = request.get_json()

    try:
        tax.name = data['name']
        tax.description = data.get('description', tax.description)
        tax.is_active = data.get('is_active', tax.is_active)

        rate_value = Decimal(str(data.get('rate', tax.rate)))
        if rate_value < 0 or rate_value > 100:
            return api_error('Tax rate must be between 0 and 100', 400)
        tax.rate = rate_value

        tax_type_raw = data.get('tax_type') or data.get('type')
        if tax_type_raw:
            try:
                tax.tax_type = TaxType(tax_type_raw)
            except Exception:
                try:
                    tax.tax_type = TaxType[tax_type_raw.upper()]
                except Exception:
                    return api_error('Invalid tax_type', 400)

        db.session.commit()

        tax_data = serialize_model(tax)
        tax_data['rate'] = float(tax.rate) if tax.rate is not None else None
        tax_data['tax_type'] = tax.tax_type.value if getattr(tax, 'tax_type', None) else None

        return api_response(
            data={'tax': tax_data},
            message='Tax updated successfully'
        )

    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update tax: {str(e)}', 500)

@tax_api_bp.route('/<int:tax_id>', methods=['DELETE'])
@require_api_key
def delete_tax(tax_id):
    """Delete tax"""
    tax = TaxCode.query.filter_by(
        id=tax_id,
        organization_id=current_user.organization_id
    ).first()

    if not tax:
        return api_error('Tax not found', 404)

    try:
        db.session.delete(tax)
        db.session.commit()

        return api_response(message='Tax deleted successfully')

    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to delete tax: {str(e)}', 500)

@tax_api_bp.route('/calculate', methods=['POST'])
@require_api_key
@validate_json_request(['amount', 'tax_id'])
def calculate_tax():
    """Calculate tax amount for given amount and tax rate"""
    data = request.get_json()

    try:
        amount = Decimal(str(data['amount']))
        tax_id = data['tax_id']

        # Get tax and default rate
        tax = TaxCode.query.filter_by(
            id=tax_id,
            organization_id=current_user.organization_id,
            is_active=True
        ).first()

        if not tax:
            return api_error('Tax not found or inactive', 404)
        tax_amount = amount * (tax.rate / Decimal('100')) if tax.rate is not None else Decimal('0')

        return api_response(data={
            'amount': float(amount),
            'tax_rate': float(tax.rate) if tax.rate is not None else None,
            'tax_amount': float(tax_amount),
            'total_amount': float(amount + tax_amount)
        })

    except ValueError:
        return api_error('Invalid amount format', 400)
    except Exception as e:
        return api_error(f'Failed to calculate tax: {str(e)}', 500)