"""
Invoice management routes for BigCapitalPy
"""

from flask import Blueprint

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('/')
def index():
    return "Invoices - Coming Soon"
