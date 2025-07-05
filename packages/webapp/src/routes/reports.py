"""
Financial Reports routes for BigCapitalPy
"""

from flask import Blueprint

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
def index():
    return "Reports - Coming Soon"
