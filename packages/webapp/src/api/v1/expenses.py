"""
Expenses API endpoints for BigCapitalPy
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from decimal import Decimal
from datetime import datetime
from sqlalchemy import desc

from packages.server.src.models import (
    Expense, ExpenseLineItem, ExpenseStatus, TaxCode
)
from packages.server.src.database import db

expenses_api_bp = Blueprint('expenses_api', __name__)


@expenses_api_bp.route('/', methods=['GET'])
@login_required
def list_expenses():
    """List expenses"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Expense.query.filter(Expense.organization_id == current_user.organization_id)
    query = query.order_by(desc(Expense.expense_date))
    expenses = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'expenses': [{
            'id': e.id,
            'expense_number': e.expense_number,
            'expense_date': e.expense_date.isoformat(),
            'vendor_id': e.vendor_id,
            'total': str(e.total),
            'status': e.status.value,
            'description': e.description
        } for e in expenses.items],
        'total': expenses.total,
        'page': expenses.page,
        'pages': expenses.pages
    })


@expenses_api_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_expense(id):
    """Get expense details"""
    expense = Expense.query.filter(
        Expense.id == id,
        Expense.organization_id == current_user.organization_id
    ).first_or_404()

    return jsonify({
        'id': expense.id,
        'expense_number': expense.expense_number,
        'expense_date': expense.expense_date.isoformat(),
        'vendor_id': expense.vendor_id,
        'subtotal': str(expense.subtotal),
        'tax_amount': str(expense.tax_amount),
        'total': str(expense.total),
        'status': expense.status.value,
        'description': expense.description,
        'line_items': [{
            'id': li.id,
            'description': li.description,
            'amount': str(li.amount),
            'account_id': li.account_id,
            'tax_amount': str(li.tax_amount or 0)
        } for li in expense.line_items]
    })


@expenses_api_bp.route('/', methods=['POST'])
@login_required
def create_expense():
    """Create an expense"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        expense = Expense(
            organization_id=current_user.organization_id,
            expense_number=data['expense_number'],
            expense_date=datetime.strptime(data['expense_date'], '%Y-%m-%d').date(),
            vendor_id=data.get('vendor_id'),
            payment_account_id=data.get('payment_account_id'),
            description=data.get('description'),
            notes=data.get('notes'),
            created_by=current_user.id
        )

        subtotal = Decimal('0')
        total_tax = Decimal('0')

        for item_data in data.get('line_items', []):
            amount = Decimal(str(item_data.get('amount', 0)))
            tax_amount = Decimal('0')

            tax_code_id = item_data.get('tax_code_id')
            if tax_code_id:
                tc = TaxCode.query.get(tax_code_id)
                if tc:
                    tax_amount = amount * (tc.rate / Decimal('100'))

            line_item = ExpenseLineItem(
                description=item_data['description'],
                amount=amount,
                account_id=item_data.get('account_id'),
                tax_code_id=tax_code_id,
                tax_amount=tax_amount
            )
            expense.line_items.append(line_item)
            subtotal += amount
            total_tax += tax_amount

        expense.subtotal = subtotal
        expense.tax_amount = total_tax
        expense.total = subtotal + total_tax

        db.session.add(expense)
        db.session.commit()

        return jsonify({'id': expense.id, 'expense_number': expense.expense_number}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
