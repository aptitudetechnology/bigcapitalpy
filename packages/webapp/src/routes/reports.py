"""
Modular Financial Reports entrypoint for BigCapitalPy
Imports and registers all report blueprints from submodules
"""

from .tax import tax_bp
from .sales import sales_bp
from .financial import financial_bp
from .expenses import expenses_bp
from .custom import custom_bp
# Add other blueprints as needed

def register_reports_blueprints(app):
    app.register_blueprint(tax_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(financial_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(custom_bp)
    # Register other blueprints as needed
