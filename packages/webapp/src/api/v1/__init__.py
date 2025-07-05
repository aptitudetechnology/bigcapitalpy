"""
BigCapitalPy REST API v1
Main API initialization and configuration
"""

from flask import Blueprint
from .auth import auth_api_bp
from .customers import customers_api_bp
from .vendors import vendors_api_bp
from .items import items_api_bp
from .invoices import invoices_api_bp
from .payments import payments_api_bp
from .accounts import accounts_api_bp
from .reports import reports_api_bp
from .organizations import organizations_api_bp

# Create API v1 blueprint
api_v1_bp = Blueprint('api_v1', __name__)

def register_api_blueprints(app):
    """Register all API v1 blueprints"""
    
    # Register API v1 sub-blueprints
    api_v1_bp.register_blueprint(auth_api_bp, url_prefix='/auth')
    api_v1_bp.register_blueprint(customers_api_bp, url_prefix='/customers')
    api_v1_bp.register_blueprint(vendors_api_bp, url_prefix='/vendors')
    api_v1_bp.register_blueprint(items_api_bp, url_prefix='/items')
    api_v1_bp.register_blueprint(invoices_api_bp, url_prefix='/invoices')
    api_v1_bp.register_blueprint(payments_api_bp, url_prefix='/payments')
    api_v1_bp.register_blueprint(accounts_api_bp, url_prefix='/accounts')
    api_v1_bp.register_blueprint(reports_api_bp, url_prefix='/reports')
    api_v1_bp.register_blueprint(organizations_api_bp, url_prefix='/organizations')
    
    # Register main API v1 blueprint
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    
    print("✅ API v1 blueprints registered successfully")
