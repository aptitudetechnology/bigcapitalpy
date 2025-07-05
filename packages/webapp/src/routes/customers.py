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
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            organization_id=current_user.organization_id
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer created successfully', 'success')
        return redirect(url_for('customers.index'))
    
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
