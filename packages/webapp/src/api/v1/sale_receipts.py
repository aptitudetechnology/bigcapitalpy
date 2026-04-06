"""
Sale Receipts API endpoints for BigCapitalPy
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from decimal import Decimal
from datetime import datetime
from sqlalchemy import desc

from packages.server.src.models import (
    SaleReceipt, SaleReceiptLineItem, SaleReceiptStatus, TaxCode
)
from packages.server.src.database import db

sale_receipts_api_bp = Blueprint('sale_receipts_api', __name__)


@sale_receipts_api_bp.route('/', methods=['GET'])
@login_required
def list_sale_receipts():
    """List sale receipts"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = SaleReceipt.query.filter(SaleReceipt.organization_id == current_user.organization_id)
    query = query.order_by(desc(SaleReceipt.receipt_date))
    receipts = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'sale_receipts': [{
            'id': r.id,
            'receipt_number': r.receipt_number,
            'receipt_date': r.receipt_date.isoformat(),
            'customer_id': r.customer_id,
            'total': str(r.total),
            'status': r.status.value
        } for r in receipts.items],
        'total': receipts.total,
        'page': receipts.page,
        'pages': receipts.pages
    })


@sale_receipts_api_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_sale_receipt(id):
    """Get sale receipt details"""
    receipt = SaleReceipt.query.filter(
        SaleReceipt.id == id,
        SaleReceipt.organization_id == current_user.organization_id
    ).first_or_404()

    return jsonify({
        'id': receipt.id,
        'receipt_number': receipt.receipt_number,
        'receipt_date': receipt.receipt_date.isoformat(),
        'customer_id': receipt.customer_id,
        'subtotal': str(receipt.subtotal),
        'tax_amount': str(receipt.tax_amount),
        'total': str(receipt.total),
        'status': receipt.status.value,
        'deposit_account_id': receipt.deposit_account_id,
        'payment_method': receipt.payment_method.value if receipt.payment_method else None,
        'notes': receipt.notes,
        'line_items': [{
            'id': li.id,
            'description': li.description,
            'quantity': str(li.quantity),
            'rate': str(li.rate),
            'amount': str(li.amount),
            'tax_amount': str(li.tax_amount or 0)
        } for li in receipt.line_items]
    })


@sale_receipts_api_bp.route('/', methods=['POST'])
@login_required
def create_sale_receipt():
    """Create a sale receipt"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        receipt = SaleReceipt(
            organization_id=current_user.organization_id,
            receipt_number=data['receipt_number'],
            receipt_date=datetime.strptime(data['receipt_date'], '%Y-%m-%d').date(),
            customer_id=data['customer_id'],
            deposit_account_id=data.get('deposit_account_id'),
            notes=data.get('notes'),
            created_by=current_user.id
        )

        subtotal = Decimal('0')
        total_tax = Decimal('0')

        for item_data in data.get('line_items', []):
            quantity = Decimal(str(item_data.get('quantity', 1)))
            rate = Decimal(str(item_data.get('rate', 0)))
            amount = quantity * rate
            tax_amount = Decimal('0')

            tax_code_id = item_data.get('tax_code_id')
            if tax_code_id:
                tc = TaxCode.query.get(tax_code_id)
                if tc:
                    tax_amount = amount * (tc.rate / Decimal('100'))

            line_item = SaleReceiptLineItem(
                description=item_data['description'],
                quantity=quantity,
                rate=rate,
                amount=amount,
                item_id=item_data.get('item_id'),
                tax_code_id=tax_code_id,
                tax_amount=tax_amount
            )
            receipt.line_items.append(line_item)
            subtotal += amount
            total_tax += tax_amount

        receipt.subtotal = subtotal
        receipt.tax_amount = total_tax
        receipt.total = subtotal + total_tax

        db.session.add(receipt)
        db.session.commit()

        return jsonify({'id': receipt.id, 'receipt_number': receipt.receipt_number}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
