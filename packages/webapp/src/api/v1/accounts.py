"""
Accounts API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from packages.server.src.models import Account, AccountType
from packages.server.src.database import db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request,
    paginate_query, get_pagination_params, serialize_model
)

accounts_api_bp = Blueprint('accounts_api', __name__)

@accounts_api_bp.route('', methods=['GET'])
@require_api_key
def list_accounts():
    """Get paginated list of accounts"""
    page, per_page = get_pagination_params()
    
    # Build query
    query = Account.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    )
    
    # Apply type filter
    account_type = request.args.get('type', '').strip()
    if account_type:
        try:
            type_enum = AccountType(account_type.lower())
            query = query.filter(Account.type == type_enum)
        except ValueError:
            pass
    
    # Apply search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            Account.name.ilike(f'%{search}%') |
            Account.code.ilike(f'%{search}%') |
            Account.description.ilike(f'%{search}%')
        )
    
    # Apply sorting
    sort_by = request.args.get('sort_by', 'code')
    sort_order = request.args.get('sort_order', 'asc')
    
    if hasattr(Account, sort_by):
        column = getattr(Account, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    
    # Paginate results
    result = paginate_query(query, page, per_page)
    
    # Serialize accounts with parent information
    accounts_data = []
    for account in result['items']:
        account_data = serialize_model(account)
        if account.parent:
            account_data['parent'] = {
                'id': account.parent.id,
                'name': account.parent.name,
                'code': account.parent.code
            }
        accounts_data.append(account_data)
    
    return api_response(data={
        'accounts': accounts_data,
        'pagination': result['pagination']
    })

@accounts_api_bp.route('/<int:account_id>', methods=['GET'])
@require_api_key
def get_account(account_id):
    """Get specific account by ID"""
    account = Account.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not account:
        return api_error('Account not found', 404)
    
    account_data = serialize_model(account)
    
    # Add parent and children information
    if account.parent:
        account_data['parent'] = serialize_model(account.parent)
    
    children_data = [serialize_model(child) for child in account.children if child.is_active]
    account_data['children'] = children_data
    
    return api_response(data={'account': account_data})

@accounts_api_bp.route('', methods=['POST'])
@require_api_key
@validate_json_request(['code', 'name', 'type'])
def create_account():
    """Create new account"""
    data = request.get_json()
    
    try:
        # Validate account type
        account_type = AccountType(data['type'].lower())
        
        # Check if code already exists
        existing = Account.query.filter_by(
            code=data['code'],
            organization_id=current_user.organization_id
        ).first()
        
        if existing:
            return api_error('Account code already exists', 409)
        
        account = Account(
            code=data['code'],
            name=data['name'],
            type=account_type,
            parent_id=data.get('parent_id'),
            description=data.get('description'),
            opening_balance=data.get('opening_balance', 0),
            current_balance=data.get('opening_balance', 0),
            organization_id=current_user.organization_id
        )
        
        db.session.add(account)
        db.session.commit()
        
        account_data = serialize_model(account)
        
        return api_response(
            data={'account': account_data},
            message='Account created successfully',
            status_code=201
        )
        
    except ValueError as e:
        return api_error(f'Invalid account type: {data.get("type")}', 400)
    except IntegrityError:
        db.session.rollback()
        return api_error('Account code already exists', 409)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to create account: {str(e)}', 500)

@accounts_api_bp.route('/<int:account_id>', methods=['PUT'])
@require_api_key
@validate_json_request(['code', 'name', 'type'])
def update_account(account_id):
    """Update existing account"""
    account = Account.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not account:
        return api_error('Account not found', 404)
    
    data = request.get_json()
    
    try:
        # Validate account type
        account_type = AccountType(data['type'].lower())
        
        # Check if code already exists (excluding current account)
        existing = Account.query.filter(
            Account.code == data['code'],
            Account.organization_id == current_user.organization_id,
            Account.id != account_id
        ).first()
        
        if existing:
            return api_error('Account code already exists', 409)
        
        # Update fields
        account.code = data['code']
        account.name = data['name']
        account.type = account_type
        account.parent_id = data.get('parent_id')
        account.description = data.get('description')
        
        # Only allow opening balance changes if no transactions exist
        if 'opening_balance' in data:
            # In a full implementation, check for existing transactions
            account.opening_balance = data['opening_balance']
        
        db.session.commit()
        
        account_data = serialize_model(account)
        
        return api_response(
            data={'account': account_data},
            message='Account updated successfully'
        )
        
    except ValueError as e:
        return api_error(f'Invalid account type: {data.get("type")}', 400)
    except IntegrityError:
        db.session.rollback()
        return api_error('Account code already exists', 409)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update account: {str(e)}', 500)

@accounts_api_bp.route('/<int:account_id>', methods=['DELETE'])
@require_api_key
def delete_account(account_id):
    """Soft delete account"""
    account = Account.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not account:
        return api_error('Account not found', 404)
    
    # Check if account has children
    if account.children:
        active_children = [child for child in account.children if child.is_active]
        if active_children:
            return api_error('Cannot delete account with active sub-accounts', 400)
    
    try:
        # Soft delete
        account.is_active = False
        db.session.commit()
        
        return api_response(message='Account deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to delete account: {str(e)}', 500)

@accounts_api_bp.route('/hierarchy', methods=['GET'])
@require_api_key
def get_account_hierarchy():
    """Get account hierarchy as nested tree structure"""
    accounts = Account.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    ).order_by(Account.code).all()
    
    def account_to_dict(account):
        return {
            'id': account.id,
            'code': account.code,
            'name': account.name,
            'type': account.type.value,
            'parent_id': account.parent_id,
            'current_balance': float(account.current_balance or 0),
            'children': []
        }
    
    # Build hierarchy
    account_dict = {acc.id: account_to_dict(acc) for acc in accounts}
    root_accounts = []
    
    for account in accounts:
        account_data = account_dict[account.id]
        if account.parent_id and account.parent_id in account_dict:
            account_dict[account.parent_id]['children'].append(account_data)
        else:
            root_accounts.append(account_data)
    
    # Group by account type
    hierarchy = {}
    for account_type in AccountType:
        hierarchy[account_type.value] = []
    
    for account_data in root_accounts:
        account_type = account_data['type']
        hierarchy[account_type].append(account_data)
    
    return api_response(data={'hierarchy': hierarchy})

@accounts_api_bp.route('/types', methods=['GET'])
@require_api_key
def get_account_types():
    """Get list of available account types"""
    types = [{'value': t.value, 'label': t.value.title()} for t in AccountType]
    return api_response(data={'types': types})

@accounts_api_bp.route('/summary', methods=['GET'])
@require_api_key
def get_accounts_summary():
    """Get account summary by type"""
    summary = {}
    
    for account_type in AccountType:
        accounts = Account.query.filter_by(
            organization_id=current_user.organization_id,
            type=account_type,
            is_active=True
        ).all()
        
        total_balance = sum(float(acc.current_balance or 0) for acc in accounts)
        
        summary[f'{account_type.value}s'] = {
            'count': len(accounts),
            'total_balance': total_balance
        }
    
    return api_response(data={'summary': summary})
