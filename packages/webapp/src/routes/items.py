"""
Items/Inventory management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from packages.server.src.models import Item
from packages.server.src.database import db

items_bp = Blueprint('items', __name__)

@items_bp.route('/')
@login_required
def index():
    """Item listing page"""
    # Get filter parameters
    search = request.args.get('search', '')
    item_type = request.args.get('type', '')
    status = request.args.get('status', '')
    
    # Build query
    query = Item.query.filter_by(organization_id=current_user.organization_id)
    
    # Apply filters
    if search:
        query = query.filter(Item.name.contains(search) | Item.sku.contains(search))
    
    if item_type:
        query = query.filter_by(type=item_type)
    
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    items = query.order_by(Item.name).all()
    
    return render_template('items/index.html', items=items)

@items_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new item"""
    if request.method == 'POST':
        item = Item(
            name=request.form.get('name'),
            sku=request.form.get('sku') or None,  # Convert empty string to None
            description=request.form.get('description'),
            type=request.form.get('type'),
            category=request.form.get('category'),
            sell_price=float(request.form.get('sell_price', 0) or 0),
            cost_price=float(request.form.get('cost_price', 0) or 0),
            quantity_on_hand=float(request.form.get('quantity_on_hand', 0) or 0),
            reorder_level=float(request.form.get('reorder_level', 0) or 0),
            unit=request.form.get('unit'),
            weight=float(request.form.get('weight', 0) or 0) if request.form.get('weight') else None,
            dimensions=request.form.get('dimensions'),
            organization_id=current_user.organization_id
        )
        
        try:
            db.session.add(item)
            db.session.commit()
            flash('Item created successfully', 'success')
            return redirect(url_for('items.show', item_id=item.id))
        except Exception as e:
            db.session.rollback()
            flash('Error creating item. SKU might already exist.', 'error')
    
    return render_template('items/new.html')

@items_bp.route('/<int:item_id>')
@login_required
def show(item_id):
    """Show item details"""
    item = Item.query.filter_by(
        id=item_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    return render_template('items/show.html', item=item)

@items_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    """Edit item"""
    item = Item.query.filter_by(
        id=item_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.sku = request.form.get('sku') or None
        item.description = request.form.get('description')
        item.type = request.form.get('type')
        item.category = request.form.get('category')
        item.sell_price = float(request.form.get('sell_price', 0) or 0)
        item.cost_price = float(request.form.get('cost_price', 0) or 0)
        item.quantity_on_hand = float(request.form.get('quantity_on_hand', 0) or 0)
        item.reorder_level = float(request.form.get('reorder_level', 0) or 0)
        item.unit = request.form.get('unit')
        item.weight = float(request.form.get('weight', 0) or 0) if request.form.get('weight') else None
        item.dimensions = request.form.get('dimensions')
        item.is_active = bool(request.form.get('is_active'))
        
        try:
            db.session.commit()
            flash('Item updated successfully', 'success')
            return redirect(url_for('items.show', item_id=item.id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating item. SKU might already exist.', 'error')
    
    return render_template('items/edit.html', item=item)

@items_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
def delete(item_id):
    """Delete item"""
    item = Item.query.filter_by(
        id=item_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    # Soft delete by setting is_active to False
    item.is_active = False
    db.session.commit()
    
    flash(f'Item "{item.name}" has been deleted', 'success')
    return redirect(url_for('items.index'))
