"""
Flask Blueprint Registration for BigCapitalPy
"""

from .dashboard import dashboard_bp
from .auth import auth_bp
from .customers import customers_bp
from .vendors import vendors_bp
from .items import items_bp
from .accounts import accounts_bp
from .reports import reports_bp
from .invoices import invoices_bp
from .financial import financial_bp
from .payments import payments_bp

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
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(invoices_bp, url_prefix='/invoices')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(financial_bp, url_prefix='/financial')
    
    print("✅ All blueprints registered successfully")
