"""
Vendor management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from packages.server.src.models import Vendor
from packages.server.src.database import db
from decimal import Decimal

vendors_bp = Blueprint('vendors', __name__)

@vendors_bp.route('/')
@login_required
def index():
    """Display list of all vendors"""
    vendors = Vendor.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('vendors/index.html', vendors=vendors)

@vendors_bp.route('/new')
@login_required
def new():
    """Show form to create new vendor"""
    return render_template('vendors/new.html')

@vendors_bp.route('/create', methods=['POST'])
@login_required
def create():
    """Create a new vendor"""
    try:
        vendor = Vendor(
            display_name=request.form.get('display_name'),
            company_name=request.form.get('company_name') or None,
            first_name=request.form.get('first_name') or None,
            last_name=request.form.get('last_name') or None,
            email=request.form.get('email') or None,
            phone=request.form.get('phone') or None,
            website=request.form.get('website') or None,
            address=request.form.get('address') or None,
            city=request.form.get('city') or None,
            state=request.form.get('state') or None,
            postal_code=request.form.get('postal_code') or None,
            country=request.form.get('country') or None,
            currency=request.form.get('currency', 'USD'),
            opening_balance=Decimal(request.form.get('opening_balance', '0') or '0'),
            current_balance=Decimal(request.form.get('opening_balance', '0') or '0'),
            tax_number=request.form.get('tax_number') or None,
            is_active=bool(request.form.get('is_active')),
            notes=request.form.get('notes') or None,
            organization_id=current_user.organization_id
        )
        
        db.session.add(vendor)
        db.session.commit()
        
        flash('Vendor created successfully!', 'success')
        return redirect(url_for('vendors.show', id=vendor.id))
        
    except Exception as e:
        current_app.logger.error(f"Error creating vendor: {str(e)}")
        flash('Error creating vendor. Please try again.', 'error')
        return render_template('vendors/new.html')

@vendors_bp.route('/<int:id>')
@login_required
def show(id):
    """Show vendor details"""
    vendor = Vendor.query.filter_by(
        id=id, 
        organization_id=current_user.organization_id
    ).first_or_404()
    return render_template('vendors/show.html', vendor=vendor)

@vendors_bp.route('/<int:id>/edit')
@login_required
def edit(id):
    """Show form to edit vendor"""
    vendor = Vendor.query.filter_by(
        id=id, 
        organization_id=current_user.organization_id
    ).first_or_404()
    return render_template('vendors/edit.html', vendor=vendor)

@vendors_bp.route('/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    """Update vendor"""
    vendor = Vendor.query.filter_by(
        id=id, 
        organization_id=current_user.organization_id
    ).first_or_404()
    
    try:
        vendor.display_name = request.form.get('display_name')
        vendor.company_name = request.form.get('company_name') or None
        vendor.first_name = request.form.get('first_name') or None
        vendor.last_name = request.form.get('last_name') or None
        vendor.email = request.form.get('email') or None
        vendor.phone = request.form.get('phone') or None
        vendor.website = request.form.get('website') or None
        vendor.address = request.form.get('address') or None
        vendor.city = request.form.get('city') or None
        vendor.state = request.form.get('state') or None
        vendor.postal_code = request.form.get('postal_code') or None
        vendor.country = request.form.get('country') or None
        vendor.currency = request.form.get('currency', 'USD')
        vendor.opening_balance = Decimal(request.form.get('opening_balance', '0') or '0')
        vendor.tax_number = request.form.get('tax_number') or None
        vendor.is_active = bool(request.form.get('is_active'))
        vendor.notes = request.form.get('notes') or None
        
        db.session.commit()
        
        flash('Vendor updated successfully!', 'success')
        return redirect(url_for('vendors.show', id=vendor.id))
        
    except Exception as e:
        current_app.logger.error(f"Error updating vendor: {str(e)}")
        flash('Error updating vendor. Please try again.', 'error')
        return render_template('vendors/edit.html', vendor=vendor)

@vendors_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete vendor"""
    vendor = Vendor.query.filter_by(
        id=id, 
        organization_id=current_user.organization_id
    ).first_or_404()
    
    try:
        vendor_name = vendor.display_name
        db.session.delete(vendor)
        db.session.commit()
        
        flash(f'Vendor "{vendor_name}" deleted successfully!', 'success')
        return redirect(url_for('vendors.index'))
        
    except Exception as e:
        current_app.logger.error(f"Error deleting vendor: {str(e)}")
        flash('Error deleting vendor. Please try again.', 'error')
        return redirect(url_for('vendors.show', id=id))
