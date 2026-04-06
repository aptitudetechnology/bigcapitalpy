"""
Item Categories management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from packages.server.src.models import ItemCategory, Item
from packages.server.src.database import db

item_categories_bp = Blueprint('item_categories', __name__)


@item_categories_bp.route('/')
@login_required
def index():
    """List all item categories"""
    categories = ItemCategory.query.filter(
        ItemCategory.organization_id == current_user.organization_id,
        ItemCategory.parent_id == None
    ).order_by(ItemCategory.name).all()

    all_categories = ItemCategory.query.filter(
        ItemCategory.organization_id == current_user.organization_id
    ).order_by(ItemCategory.name).all()

    return render_template('item_categories/index.html',
                         categories=categories,
                         all_categories=all_categories)


@item_categories_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new item category"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        parent_id = request.form.get('parent_id') or None

        if not name:
            flash('Category name is required.', 'error')
            return redirect(url_for('item_categories.new'))

        category = ItemCategory(
            name=name,
            description=description,
            parent_id=parent_id,
            organization_id=current_user.organization_id
        )

        try:
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
            return redirect(url_for('item_categories.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating category: {str(e)}', 'error')

    parent_categories = ItemCategory.query.filter(
        ItemCategory.organization_id == current_user.organization_id
    ).order_by(ItemCategory.name).all()

    return render_template('item_categories/new.html', parent_categories=parent_categories)


@item_categories_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit item category"""
    category = ItemCategory.query.filter(
        ItemCategory.id == id,
        ItemCategory.organization_id == current_user.organization_id
    ).first_or_404()

    if request.method == 'POST':
        category.name = request.form.get('name', '').strip()
        category.description = request.form.get('description', '').strip()
        parent_id = request.form.get('parent_id') or None
        # Prevent setting self as parent
        if parent_id and int(parent_id) == category.id:
            flash('A category cannot be its own parent.', 'error')
            return redirect(url_for('item_categories.edit', id=id))
        category.parent_id = parent_id

        try:
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('item_categories.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating category: {str(e)}', 'error')

    parent_categories = ItemCategory.query.filter(
        ItemCategory.organization_id == current_user.organization_id,
        ItemCategory.id != id
    ).order_by(ItemCategory.name).all()

    return render_template('item_categories/edit.html',
                         category=category,
                         parent_categories=parent_categories)


@item_categories_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete item category"""
    category = ItemCategory.query.filter(
        ItemCategory.id == id,
        ItemCategory.organization_id == current_user.organization_id
    ).first_or_404()

    # Check for items using this category
    item_count = Item.query.filter(Item.category_id == id).count()
    if item_count > 0:
        flash(f'Cannot delete category with {item_count} items. Reassign items first.', 'error')
        return redirect(url_for('item_categories.index'))

    # Check for subcategories
    if category.subcategories:
        flash('Cannot delete category with subcategories. Delete subcategories first.', 'error')
        return redirect(url_for('item_categories.index'))

    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'error')

    return redirect(url_for('item_categories.index'))
