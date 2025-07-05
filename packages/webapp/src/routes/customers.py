"""
Customer management routes for BigCapitalPy
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from packages.server.src.models import Customer
from packages.server.src.database import db

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/')
@login_required
def index():
    """Customer listing page"""
    customers = Customer.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    ).order_by(Customer.display_name).all()
    
    return render_template('customers/index.html', customers=customers)

@customers_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new customer"""
    if request.method == 'POST':
        customer = Customer(
            display_name=request.form.get('display_name'),
            company_name=request.form.get('company_name'),
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            website=request.form.get('website'),
            billing_address=request.form.get('billing_address'),
            billing_city=request.form.get('billing_city'),
            billing_state=request.form.get('billing_state'),
            billing_postal_code=request.form.get('billing_postal_code'),
            billing_country=request.form.get('billing_country'),
            tax_number=request.form.get('tax_number'),
            currency=request.form.get('currency', 'USD'),
            credit_limit=float(request.form.get('credit_limit', 0) or 0),
            notes=request.form.get('notes'),
            organization_id=current_user.organization_id
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer created successfully', 'success')
        return redirect(url_for('customers.show', customer_id=customer.id))
    
    return render_template('customers/new.html')

@customers_bp.route('/<int:customer_id>')
@login_required
def show(customer_id):
    """Show customer details"""
    customer = Customer.query.filter_by(
        id=customer_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    return render_template('customers/show.html', customer=customer)

@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    """Edit customer"""
    customer = Customer.query.filter_by(
        id=customer_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    if request.method == 'POST':
        customer.display_name = request.form.get('display_name')
        customer.company_name = request.form.get('company_name')
        customer.first_name = request.form.get('first_name')
        customer.last_name = request.form.get('last_name')
        customer.email = request.form.get('email')
        customer.phone = request.form.get('phone')
        customer.website = request.form.get('website')
        customer.billing_address = request.form.get('billing_address')
        customer.billing_city = request.form.get('billing_city')
        customer.billing_state = request.form.get('billing_state')
        customer.billing_postal_code = request.form.get('billing_postal_code')
        customer.billing_country = request.form.get('billing_country')
        customer.tax_number = request.form.get('tax_number')
        customer.currency = request.form.get('currency', 'USD')
        customer.credit_limit = float(request.form.get('credit_limit', 0) or 0)
        customer.notes = request.form.get('notes')
        customer.is_active = bool(request.form.get('is_active'))
        
        db.session.commit()
        flash('Customer updated successfully', 'success')
        return redirect(url_for('customers.show', customer_id=customer.id))
    
    return render_template('customers/edit.html', customer=customer)

@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete(customer_id):
    """Delete customer"""
    customer = Customer.query.filter_by(
        id=customer_id,
        organization_id=current_user.organization_id
    ).first_or_404()
    
    # Soft delete by setting is_active to False
    customer.is_active = False
    db.session.commit()
    
    flash(f'Customer "{customer.display_name}" has been deleted', 'success')
    return redirect(url_for('customers.index'))
