"""
Bills API endpoints for BigCapitalPy
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from decimal import Decimal
from datetime import datetime
from sqlalchemy import desc

from packages.server.src.models import (
    Bill, BillLineItem, Vendor, BillStatus, TaxCode
)
from packages.server.src.database import db

bills_api_bp = Blueprint('bills_api', __name__)


@bills_api_bp.route('/', methods=['GET'])
@login_required
def list_bills():
    """List bills with optional filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    vendor_id = request.args.get('vendor_id')

    query = Bill.query.filter(Bill.organization_id == current_user.organization_id)
    if status:
        query = query.filter(Bill.status == status)
    if vendor_id:
        query = query.filter(Bill.vendor_id == vendor_id)

    query = query.order_by(desc(Bill.bill_date))
    bills = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'bills': [{
            'id': b.id,
            'bill_number': b.bill_number,
            'vendor_id': b.vendor_id,
            'vendor_name': b.vendor.display_name,
            'bill_date': b.bill_date.isoformat(),
            'due_date': b.due_date.isoformat(),
            'subtotal': str(b.subtotal),
            'tax_amount': str(b.tax_amount),
            'total': str(b.total),
            'paid_amount': str(b.paid_amount),
            'balance': str(b.balance),
            'status': b.status.value
        } for b in bills.items],
        'total': bills.total,
        'page': bills.page,
        'pages': bills.pages
    })


@bills_api_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_bill(id):
    """Get bill details"""
    bill = Bill.query.filter(
        Bill.id == id,
        Bill.organization_id == current_user.organization_id
    ).first_or_404()

    return jsonify({
        'id': bill.id,
        'bill_number': bill.bill_number,
        'vendor_id': bill.vendor_id,
        'vendor_name': bill.vendor.display_name,
        'bill_date': bill.bill_date.isoformat(),
        'due_date': bill.due_date.isoformat(),
        'subtotal': str(bill.subtotal),
        'tax_amount': str(bill.tax_amount),
        'total': str(bill.total),
        'paid_amount': str(bill.paid_amount),
        'balance': str(bill.balance),
        'status': bill.status.value,
        'line_items': [{
            'id': li.id,
            'description': li.description,
            'quantity': str(li.quantity),
            'rate': str(li.rate),
            'amount': str(li.amount),
            'tax_amount': str(li.tax_amount or 0),
            'account_id': li.account_id
        } for li in bill.line_items]
    })


@bills_api_bp.route('/', methods=['POST'])
@login_required
def create_bill():
    """Create a new bill"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        bill = Bill(
            organization_id=current_user.organization_id,
            bill_number=data['bill_number'],
            vendor_id=data['vendor_id'],
            bill_date=datetime.strptime(data['bill_date'], '%Y-%m-%d').date(),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            vendor_bill_number=data.get('vendor_bill_number'),
            reference=data.get('reference'),
            notes=data.get('notes')
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

            line_item = BillLineItem(
                description=item_data['description'],
                quantity=quantity,
                rate=rate,
                amount=amount,
                item_id=item_data.get('item_id'),
                account_id=item_data.get('account_id'),
                tax_code_id=tax_code_id,
                tax_amount=tax_amount
            )
            bill.line_items.append(line_item)
            subtotal += amount
            total_tax += tax_amount

        bill.subtotal = subtotal
        bill.tax_amount = total_tax
        bill.total = subtotal + total_tax
        bill.balance = bill.total

        db.session.add(bill)
        db.session.commit()

        return jsonify({'id': bill.id, 'bill_number': bill.bill_number}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bills_api_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_bill(id):
    """Delete a draft bill"""
    bill = Bill.query.filter(
        Bill.id == id,
        Bill.organization_id == current_user.organization_id
    ).first_or_404()

    if bill.status != BillStatus.DRAFT:
        return jsonify({'error': 'Only draft bills can be deleted'}), 400

    db.session.delete(bill)
    db.session.commit()
    return jsonify({'message': 'Bill deleted'}), 200
