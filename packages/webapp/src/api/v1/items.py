"""
Items API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from packages.server.src.models import Item, Account
from packages.server.src.database import db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request,
    paginate_query, get_pagination_params, serialize_model
)

items_api_bp = Blueprint('items_api', __name__)

@items_api_bp.route('', methods=['GET'])
@require_api_key
def list_items():
    """Get paginated list of items"""
    page, per_page = get_pagination_params()
    
    # Build query
    query = Item.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    )
    
    # Apply search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            Item.name.ilike(f'%{search}%') |
            Item.sku.ilike(f'%{search}%') |
            Item.description.ilike(f'%{search}%')
        )
    
    # Apply category filter
    category = request.args.get('category', '').strip()
    if category:
        query = query.filter(Item.category.ilike(f'%{category}%'))
    
    # Apply type filter
    item_type = request.args.get('type', '').strip()
    if item_type:
        query = query.filter(Item.type == item_type)
    
    # Apply sorting
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    if hasattr(Item, sort_by):
        column = getattr(Item, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    
    # Paginate results
    result = paginate_query(query, page, per_page)
    
    # Serialize items with account information
    items_data = []
    for item in result['items']:
        item_data = serialize_model(item)
        
        # Add account information
        if item.income_account:
            item_data['income_account'] = {
                'id': item.income_account.id,
                'name': item.income_account.name,
                'code': item.income_account.code
            }
        if item.expense_account:
            item_data['expense_account'] = {
                'id': item.expense_account.id,
                'name': item.expense_account.name,
                'code': item.expense_account.code
            }
        if item.inventory_account:
            item_data['inventory_account'] = {
                'id': item.inventory_account.id,
                'name': item.inventory_account.name,
                'code': item.inventory_account.code
            }
        
        items_data.append(item_data)
    
    return api_response(data={
        'items': items_data,
        'pagination': result['pagination']
    })

@items_api_bp.route('/<int:item_id>', methods=['GET'])
@require_api_key
def get_item(item_id):
    """Get specific item by ID"""
    item = Item.query.filter_by(
        id=item_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not item:
        return api_error('Item not found', 404)
    
    item_data = serialize_model(item)
    
    # Add account information
    if item.income_account:
        item_data['income_account'] = serialize_model(item.income_account)
    if item.expense_account:
        item_data['expense_account'] = serialize_model(item.expense_account)
    if item.inventory_account:
        item_data['inventory_account'] = serialize_model(item.inventory_account)
    
    return api_response(data={'item': item_data})

@items_api_bp.route('', methods=['POST'])
@require_api_key
@validate_json_request(['name'])
def create_item():
    """Create new item"""
    data = request.get_json()
    
    try:
        item = Item(
            name=data['name'],
            sku=data.get('sku'),
            description=data.get('description'),
            sell_price=data.get('sell_price', 0),
            cost_price=data.get('cost_price', 0),
            quantity_on_hand=data.get('quantity_on_hand', 0),
            reorder_level=data.get('reorder_level', 0),
            type=data.get('type', 'inventory'),
            category=data.get('category'),
            unit=data.get('unit'),
            weight=data.get('weight'),
            dimensions=data.get('dimensions'),
            income_account_id=data.get('income_account_id'),
            expense_account_id=data.get('expense_account_id'),
            inventory_account_id=data.get('inventory_account_id'),
            organization_id=current_user.organization_id
        )
        
        db.session.add(item)
        db.session.commit()
        
        item_data = serialize_model(item)
        
        return api_response(
            data={'item': item_data},
            message='Item created successfully',
            status_code=201
        )
        
    except IntegrityError:
        db.session.rollback()
        return api_error('An item with this SKU already exists', 409)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to create item: {str(e)}', 500)

@items_api_bp.route('/<int:item_id>', methods=['PUT'])
@require_api_key
@validate_json_request(['name'])
def update_item(item_id):
    """Update existing item"""
    item = Item.query.filter_by(
        id=item_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not item:
        return api_error('Item not found', 404)
    
    data = request.get_json()
    
    try:
        # Update fields
        item.name = data['name']
        item.sku = data.get('sku')
        item.description = data.get('description')
        item.sell_price = data.get('sell_price', item.sell_price)
        item.cost_price = data.get('cost_price', item.cost_price)
        item.quantity_on_hand = data.get('quantity_on_hand', item.quantity_on_hand)
        item.reorder_level = data.get('reorder_level', item.reorder_level)
        item.type = data.get('type', item.type)
        item.category = data.get('category')
        item.unit = data.get('unit')
        item.weight = data.get('weight')
        item.dimensions = data.get('dimensions')
        item.income_account_id = data.get('income_account_id')
        item.expense_account_id = data.get('expense_account_id')
        item.inventory_account_id = data.get('inventory_account_id')
        
        db.session.commit()
        
        item_data = serialize_model(item)
        
        return api_response(
            data={'item': item_data},
            message='Item updated successfully'
        )
        
    except IntegrityError:
        db.session.rollback()
        return api_error('An item with this SKU already exists', 409)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update item: {str(e)}', 500)

@items_api_bp.route('/<int:item_id>', methods=['DELETE'])
@require_api_key
def delete_item(item_id):
    """Soft delete item"""
    item = Item.query.filter_by(
        id=item_id,
        organization_id=current_user.organization_id
    ).first()
    
    if not item:
        return api_error('Item not found', 404)
    
    try:
        # Soft delete
        item.is_active = False
        db.session.commit()
        
        return api_response(message='Item deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to delete item: {str(e)}', 500)

@items_api_bp.route('/search', methods=['GET'])
@require_api_key
def search_items():
    """Search items by name, SKU, or description"""
    query_str = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 10)), 50)
    
    if not query_str:
        return api_response(data={'items': []})
    
    items = Item.query.filter(
        Item.organization_id == current_user.organization_id,
        Item.is_active == True,
        (Item.name.ilike(f'%{query_str}%') |
         Item.sku.ilike(f'%{query_str}%') |
         Item.description.ilike(f'%{query_str}%'))
    ).limit(limit).all()
    
    items_data = [
        {
            'id': item.id,
            'name': item.name,
            'sku': item.sku,
            'description': item.description,
            'sell_price': float(item.sell_price or 0),
            'unit': item.unit
        }
        for item in items
    ]
    
    return api_response(data={'items': items_data})

@items_api_bp.route('/categories', methods=['GET'])
@require_api_key
def get_categories():
    """Get list of item categories"""
    categories = db.session.query(Item.category).filter(
        Item.organization_id == current_user.organization_id,
        Item.category.isnot(None),
        Item.category != ''
    ).distinct().all()
    
    category_list = [cat[0] for cat in categories if cat[0]]
    
    return api_response(data={'categories': category_list})

@items_api_bp.route('/low-stock', methods=['GET'])
@require_api_key
def get_low_stock_items():
    """Get items with low stock (below reorder level)"""
    items = Item.query.filter(
        Item.organization_id == current_user.organization_id,
        Item.is_active == True,
        Item.quantity_on_hand <= Item.reorder_level,
        Item.reorder_level > 0
    ).all()
    
    items_data = [
        {
            'id': item.id,
            'name': item.name,
            'sku': item.sku,
            'quantity_on_hand': float(item.quantity_on_hand or 0),
            'reorder_level': float(item.reorder_level or 0)
        }
        for item in items
    ]
    
    return api_response(data={'items': items_data})
