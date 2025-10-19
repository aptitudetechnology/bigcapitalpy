"""
Banking API endpoints for transactions and reconciliation
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from packages.server.src.models import BankAccount, BankTransaction, db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request,
    paginate_query, get_pagination_params, serialize_model
)

banking_api_bp = Blueprint('banking_api', __name__)

@banking_api_bp.route('/accounts/<int:account_id>/transactions', methods=['GET'])
@require_api_key
def list_transactions(account_id):
    """Get paginated list of bank transactions for an account"""
    # Verify account ownership
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first()

    if not bank_account:
        return api_error('Bank account not found', 404)

    page, per_page = get_pagination_params()

    # Build query
    query = BankTransaction.query.filter_by(account_id=account_id)

    # Apply reconciliation filter
    reconciled = request.args.get('reconciled')
    if reconciled is not None:
        is_reconciled = reconciled.lower() == 'true'
        query = query.filter(BankTransaction.is_reconciled == is_reconciled)

    # Apply date range filter
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date:
        query = query.filter(BankTransaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(BankTransaction.transaction_date <= end_date)

    # Apply search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(BankTransaction.description.ilike(f'%{search}%'))

    # Apply sorting
    sort_by = request.args.get('sort_by', 'transaction_date')
    sort_order = request.args.get('sort_order', 'desc')

    if hasattr(BankTransaction, sort_by):
        column = getattr(BankTransaction, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # Paginate results
    result = paginate_query(query, page, per_page)

    # Serialize transactions
    transactions_data = []
    for transaction in result['items']:
        transaction_data = serialize_model(transaction)
        transaction_data['reconciled_by'] = serialize_model(transaction.reconciled_by) if transaction.reconciled_by else None
        transactions_data.append(transaction_data)

    return api_response(data={
        'transactions': transactions_data,
        'pagination': result['pagination'],
        'account': serialize_model(bank_account)
    })

@banking_api_bp.route('/accounts/<int:account_id>/transactions/<int:transaction_id>', methods=['GET'])
@require_api_key
def get_transaction(account_id, transaction_id):
    """Get specific bank transaction"""
    # Verify account ownership
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first()

    if not bank_account:
        return api_error('Bank account not found', 404)

    transaction = BankTransaction.query.filter_by(
        id=transaction_id,
        account_id=account_id
    ).first()

    if not transaction:
        return api_error('Transaction not found', 404)

    transaction_data = serialize_model(transaction)
    transaction_data['reconciled_by'] = serialize_model(transaction.reconciled_by) if transaction.reconciled_by else None

    return api_response(data={'transaction': transaction_data})

@banking_api_bp.route('/accounts/<int:account_id>/transactions/<int:transaction_id>/reconcile', methods=['POST'])
@require_api_key
@validate_json_request()
def reconcile_transaction(account_id, transaction_id):
    """Mark a bank transaction as reconciled"""
    # Verify account ownership
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first()

    if not bank_account:
        return api_error('Bank account not found', 404)

    transaction = BankTransaction.query.filter_by(
        id=transaction_id,
        account_id=account_id
    ).first()

    if not transaction:
        return api_error('Transaction not found', 404)

    if transaction.is_reconciled:
        return api_error('Transaction is already reconciled', 400)

    try:
        transaction.is_reconciled = True
        transaction.reconciled_at = db.func.now()
        transaction.reconciled_by_id = current_user.id
        db.session.commit()

        transaction_data = serialize_model(transaction)
        transaction_data['reconciled_by'] = serialize_model(transaction.reconciled_by)

        return api_response(
            data={'transaction': transaction_data},
            message='Transaction reconciled successfully'
        )

    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to reconcile transaction: {str(e)}', 500)

@banking_api_bp.route('/accounts/<int:account_id>/transactions/<int:transaction_id>/unreconcile', methods=['POST'])
@require_api_key
@validate_json_request()
def unreconcile_transaction(account_id, transaction_id):
    """Mark a bank transaction as unreconciled"""
    # Verify account ownership
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first()

    if not bank_account:
        return api_error('Bank account not found', 404)

    transaction = BankTransaction.query.filter_by(
        id=transaction_id,
        account_id=account_id
    ).first()

    if not transaction:
        return api_error('Transaction not found', 404)

    if not transaction.is_reconciled:
        return api_error('Transaction is not reconciled', 400)

    try:
        transaction.is_reconciled = False
        transaction.reconciled_at = None
        transaction.reconciled_by_id = None
        db.session.commit()

        transaction_data = serialize_model(transaction)
        transaction_data['reconciled_by'] = None

        return api_response(
            data={'transaction': transaction_data},
            message='Transaction unreconciled successfully'
        )

    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to unreconcile transaction: {str(e)}', 500)

@banking_api_bp.route('/accounts/<int:account_id>/reconcile', methods=['POST'])
@require_api_key
@validate_json_request(['transaction_ids'])
def bulk_reconcile(account_id):
    """Bulk reconcile multiple transactions"""
    # Verify account ownership
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first()

    if not bank_account:
        return api_error('Bank account not found', 404)

    data = request.get_json()
    transaction_ids = data.get('transaction_ids', [])

    if not transaction_ids:
        return api_error('No transaction IDs provided', 400)

    try:
        # Update transactions
        updated_count = BankTransaction.query.filter(
            BankTransaction.id.in_(transaction_ids),
            BankTransaction.account_id == account_id,
            BankTransaction.is_reconciled == False
        ).update({
            'is_reconciled': True,
            'reconciled_at': db.func.now(),
            'reconciled_by_id': current_user.id
        })

        db.session.commit()

        return api_response(
            data={'reconciled_count': updated_count},
            message=f'Successfully reconciled {updated_count} transactions'
        )

    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to reconcile transactions: {str(e)}', 500)

@banking_api_bp.route('/accounts/<int:account_id>/reconciliation-summary', methods=['GET'])
@require_api_key
def reconciliation_summary(account_id):
    """Get reconciliation summary for a bank account"""
    # Verify account ownership
    bank_account = BankAccount.query.filter_by(
        id=account_id,
        organization_id=current_user.organization_id
    ).first()

    if not bank_account:
        return api_error('Bank account not found', 404)

    # Get reconciliation statistics
    from sqlalchemy import func

    stats = db.session.query(
        func.count(BankTransaction.id).label('total_transactions'),
        func.sum(BankTransaction.amount).label('total_amount'),
        func.count(db.case((BankTransaction.is_reconciled == True, 1))).label('reconciled_count'),
        func.sum(db.case((BankTransaction.is_reconciled == True, BankTransaction.amount), else_=0)).label('reconciled_amount')
    ).filter(BankTransaction.account_id == account_id).first()

    summary = {
        'account_id': account_id,
        'account_balance': float(bank_account.balance or 0),
        'total_transactions': stats.total_transactions or 0,
        'total_amount': float(stats.total_amount or 0),
        'reconciled_transactions': stats.reconciled_count or 0,
        'reconciled_amount': float(stats.reconciled_amount or 0),
        'unreconciled_transactions': (stats.total_transactions or 0) - (stats.reconciled_count or 0),
        'unreconciled_amount': float(stats.total_amount or 0) - float(stats.reconciled_amount or 0),
        'reconciled_balance': float(bank_account.balance or 0) - (float(stats.total_amount or 0) - float(stats.reconciled_amount or 0))
    }

    return api_response(data={'summary': summary})