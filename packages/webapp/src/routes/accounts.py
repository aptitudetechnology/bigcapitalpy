"""
Accounts blueprint for BigCapitalPy.
Handles Chart of Accounts and related operations.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
# You'll likely need to import models and db here later
# from packages.server.src.models import Account, AccountType
# from packages.server.src.database import db

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/')
@login_required
def index():
    """
    Chart of Accounts listing page.
    """
    # Placeholder data for now. You'll replace this with actual database queries.
    accounts = [
        {'id': 1, 'code': '1000', 'name': 'Cash on Hand', 'type': 'Asset', 'balance': 1500.00},
        {'id': 2, 'code': '4000', 'name': 'Sales Revenue', 'type': 'Income', 'balance': 10000.00},
    ]
    return render_template('accounts/index.html', accounts=accounts)

# Add other account-related routes as needed (e.g., /new, /<int:id>, /edit, /delete)
