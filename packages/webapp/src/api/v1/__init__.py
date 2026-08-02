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
from .banking import banking_api_bp
from .journal import journal_api_bp
from .tax import tax_api_bp
from .bills import bills_api_bp
from .expenses import expenses_api_bp
from .sale_receipts import sale_receipts_api_bp

# Create API v1 blueprint
api_v1_bp = Blueprint('api_v1', __name__)

# api_v1_bp is a module-level singleton, so wiring its sub-blueprints is a
# once-per-process operation. See the equivalent guard in routes/reports/__init__.py:
# Flask forbids setup methods on an already-registered blueprint, so repeating this
# on a second create_app() raised AssertionError. Registering the same blueprint
# object onto additional app instances is fine.
_sub_blueprints_attached = False


def register_api_blueprints(app):
    """Register all API v1 blueprints"""
    global _sub_blueprints_attached

    if not _sub_blueprints_attached:
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
        api_v1_bp.register_blueprint(banking_api_bp, url_prefix='/banking')
        api_v1_bp.register_blueprint(journal_api_bp, url_prefix='/journal')
        api_v1_bp.register_blueprint(tax_api_bp, url_prefix='/tax')
        api_v1_bp.register_blueprint(bills_api_bp, url_prefix='/bills')
        api_v1_bp.register_blueprint(expenses_api_bp, url_prefix='/expenses')
        api_v1_bp.register_blueprint(sale_receipts_api_bp, url_prefix='/sale-receipts')
        _sub_blueprints_attached = True

    # Register main API v1 blueprint
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    print("✅ API v1 blueprints registered successfully")
