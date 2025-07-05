"""
Flask Blueprint Registration for BigCapitalPy
"""

from flask import Blueprint
from .dashboard import dashboard_bp
from .auth import auth_bp
from .customers import customers_bp
from .vendors import vendors_bp
from .items import items_bp
from .accounts import accounts_bp

def register_blueprints(app):
    """Register all application blueprints"""
    
    # Authentication routes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Main application routes
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(vendors_bp, url_prefix='/vendors')
    app.register_blueprint(items_bp, url_prefix='/items')
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    
    # Create basic invoices and reports routes (placeholders)
    invoices_bp = Blueprint('invoices', __name__)
    reports_bp = Blueprint('reports', __name__)
    
    @invoices_bp.route('/')
    def index():
        return "Invoices - Coming Soon"
    
    @reports_bp.route('/')
    def index():
        return "Reports - Coming Soon"
    
    app.register_blueprint(invoices_bp, url_prefix='/invoices')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    print("✅ All blueprints registered successfully")
