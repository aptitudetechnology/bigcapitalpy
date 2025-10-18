"""
Tax API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from packages.server.src.models import Tax, TaxRate, db
from packages.webapp.src.api.utils import (
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
    query = Tax.query.filter_by(organization_id=current_user.organization_id)

    # Apply filters
    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter(Tax.is_active == (is_active.lower() == 'true'))

    # Apply search
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            Tax.name.ilike(f'%{search}%') |
            Tax.description.ilike(f'%{search}%')
        )

    # Apply sorting
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    if hasattr(Tax, sort_by):
        column = getattr(Tax, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # Paginate results
    result = paginate_query(query, page, per_page)

    # Serialize taxes with rates
    taxes_data = []
    for tax in result['items']:
        tax_data = serialize_model(tax)

        # Add tax rates
        rates_data = []
        for rate in tax.rates:
            rate_data = serialize_model(rate)
            rates_data.append(rate_data)

        tax_data['rates'] = rates_data
        taxes_data.append(tax_data)

    return api_response(data={
        'taxes': taxes_data,
        'pagination': result['pagination']
    })

@tax_api_bp.route('/<int:tax_id>', methods=['GET'])
@require_api_key
def get_tax(tax_id):
    """Get specific tax with rates"""
    tax = Tax.query.filter_by(
        id=tax_id,
        organization_id=current_user.organization_id
    ).first()

    if not tax:
        return api_error('Tax not found', 404)

    tax_data = serialize_model(tax)

    # Add tax rates
    rates_data = []
    for rate in tax.rates:
        rate_data = serialize_model(rate)
        rates_data.append(rate_data)

    tax_data['rates'] = rates_data

    return api_response(data={'tax': tax_data})

@tax_api_bp.route('', methods=['POST'])
@require_api_key
@validate_json_request(['name', 'type'])
def create_tax():
    """Create new tax with rates"""
    data = request.get_json()

    try:
        # Create tax
        tax = Tax(
            name=data['name'],
            description=data.get('description', ''),
            type=data['type'],  # 'sales' or 'purchase'
            is_active=data.get('is_active', True),
            organization_id=current_user.organization_id
        )

        # Process tax rates
        rates_data = data.get('rates', [])
        if not rates_data:
            return api_error('Tax must have at least one rate', 400)

        for rate_data in rates_data:
            rate_value = Decimal(str(rate_data.get('rate', 0)))
            if rate_value < 0 or rate_value > 100:
                return api_error('Tax rate must be between 0 and 100', 400)

            tax_rate = TaxRate(
                name=rate_data.get('name', ''),
                rate=rate_value,
                is_default=rate_data.get('is_default', False)
            )

            tax.rates.append(tax_rate)

        # Ensure only one default rate
        default_rates = [r for r in tax.rates if r.is_default]
        if len(default_rates) > 1:
            return api_error('Only one tax rate can be marked as default', 400)

        # If no default set, make first rate default
        if not default_rates:
            tax.rates[0].is_default = True

        db.session.add(tax)
        db.session.commit()

        # Return created tax
        tax_data = serialize_model(tax)

        rates_data = []
        for rate in tax.rates:
            rate_data = serialize_model(rate)
            rates_data.append(rate_data)

        tax_data['rates'] = rates_data

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
@validate_json_request(['name', 'type'])
def update_tax(tax_id):
    """Update existing tax"""
    tax = Tax.query.filter_by(
        id=tax_id,
        organization_id=current_user.organization_id
    ).first()

    if not tax:
        return api_error('Tax not found', 404)

    data = request.get_json()

    try:
        # Update basic fields
        tax.name = data['name']
        tax.description = data.get('description', tax.description)
        tax.type = data['type']
        tax.is_active = data.get('is_active', tax.is_active)

        # Update tax rates
        rates_data = data.get('rates', [])
        if not rates_data:
            return api_error('Tax must have at least one rate', 400)

        # Remove existing rates
        TaxRate.query.filter_by(tax_id=tax_id).delete()

        # Add new rates
        for rate_data in rates_data:
            rate_value = Decimal(str(rate_data.get('rate', 0)))
            if rate_value < 0 or rate_value > 100:
                return api_error('Tax rate must be between 0 and 100', 400)

            tax_rate = TaxRate(
                tax_id=tax_id,
                name=rate_data.get('name', ''),
                rate=rate_value,
                is_default=rate_data.get('is_default', False)
            )

            db.session.add(tax_rate)

        # Ensure only one default rate
        default_rates = [r for r in rates_data if r.get('is_default', False)]
        if len(default_rates) > 1:
            return api_error('Only one tax rate can be marked as default', 400)

        # If no default set, make first rate default
        if not default_rates:
            rates_data[0]['is_default'] = True

        db.session.commit()

        # Return updated tax
        tax_data = serialize_model(tax)

        rates_data = []
        for rate in tax.rates:
            rate_data = serialize_model(rate)
            rates_data.append(rate_data)

        tax_data['rates'] = rates_data

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
    tax = Tax.query.filter_by(
        id=tax_id,
        organization_id=current_user.organization_id
    ).first()

    if not tax:
        return api_error('Tax not found', 404)

    try:
        # Delete tax rates first
        TaxRate.query.filter_by(tax_id=tax_id).delete()

        # Delete tax
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
        tax = Tax.query.filter_by(
            id=tax_id,
            organization_id=current_user.organization_id,
            is_active=True
        ).first()

        if not tax:
            return api_error('Tax not found or inactive', 404)

        # Get default rate
        default_rate = None
        for rate in tax.rates:
            if rate.is_default:
                default_rate = rate
                break

        if not default_rate:
            return api_error('No default tax rate found for this tax', 400)

        # Calculate tax amount
        tax_amount = amount * (default_rate.rate / Decimal('100'))

        return api_response(data={
            'amount': float(amount),
            'tax_rate': float(default_rate.rate),
            'tax_amount': float(tax_amount),
            'total_amount': float(amount + tax_amount)
        })

    except ValueError:
        return api_error('Invalid amount format', 400)
    except Exception as e:
        return api_error(f'Failed to calculate tax: {str(e)}', 500)