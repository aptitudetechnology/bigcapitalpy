"""
Vendor management routes for BigCapitalPy
"""

from flask import Blueprint

vendors_bp = Blueprint('vendors', __name__)

@vendors_bp.route('/')
def index():
    return "Vendors - Coming Soon"
