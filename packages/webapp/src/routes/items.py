"""
Items/Inventory management routes for BigCapitalPy
"""

from flask import Blueprint

items_bp = Blueprint('items', __name__)

@items_bp.route('/')
def index():
    return "Items - Coming Soon"
