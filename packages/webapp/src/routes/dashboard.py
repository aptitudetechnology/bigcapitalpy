"""
Dashboard routes for BigCapitalPy
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from packages.server.src.models import Customer, Vendor, Invoice, Account
from packages.server.src.database import db
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard view"""
    
    # Get key metrics for dashboard
    org_id = current_user.organization_id
    
    # Customer metrics
    total_customers = Customer.query.filter_by(organization_id=org_id, is_active=True).count()
    
    # Vendor metrics
    total_vendors = Vendor.query.filter_by(organization_id=org_id, is_active=True).count()
    
    # Invoice metrics
    total_invoices = Invoice.query.filter_by(organization_id=org_id).count()
    pending_invoices = Invoice.query.filter_by(organization_id=org_id).filter(
        Invoice.balance > 0
    ).count()
    
    # Financial metrics
    total_receivables = db.session.query(func.sum(Invoice.balance)).filter_by(
        organization_id=org_id
    ).scalar() or 0
    
    # Recent invoices
    recent_invoices = Invoice.query.filter_by(organization_id=org_id).order_by(
        Invoice.created_at.desc()
    ).limit(5).all()
    
    dashboard_data = {
        'total_customers': total_customers,
        'total_vendors': total_vendors,
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'total_receivables': float(total_receivables),
        'recent_invoices': recent_invoices
    }
    
    return render_template('dashboard/index.html', data=dashboard_data)

@dashboard_bp.route('/api/metrics')
@login_required
def api_metrics():
    """API endpoint for dashboard metrics (for AJAX updates)"""
    
    org_id = current_user.organization_id
    
    # Calculate monthly sales trend (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_sales = db.session.query(
        func.date_trunc('month', Invoice.invoice_date).label('month'),
        func.sum(Invoice.total).label('total')
    ).filter(
        Invoice.organization_id == org_id,
        Invoice.invoice_date >= six_months_ago
    ).group_by('month').order_by('month').all()
    
    sales_data = [
        {
            'month': sale.month.strftime('%Y-%m'),
            'total': float(sale.total or 0)
        }
        for sale in monthly_sales
    ]
    
    return jsonify({
        'monthly_sales': sales_data,
        'last_updated': datetime.now().isoformat()
    })
