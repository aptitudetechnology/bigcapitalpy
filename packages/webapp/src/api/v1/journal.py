"""
Journal Entries API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from decimal import Decimal
from packages.server.src.models import JournalEntry, JournalLineItem, Account, db
from ..utils import (
    api_response, api_error, require_api_key, validate_json_request,
    paginate_query, get_pagination_params, serialize_model
)

journal_api_bp = Blueprint('journal_api', __name__)

@journal_api_bp.route('', methods=['GET'])
@require_api_key
def list_journal_entries():
    """Get paginated list of journal entries"""
    page, per_page = get_pagination_params()

    # Build query
    query = JournalEntry.query.filter_by(
        organization_id=current_user.organization_id
    )

    # Apply filters
    source_type = request.args.get('source_type')
    if source_type:
        query = query.filter(JournalEntry.source_type == source_type)

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date:
        query = query.filter(JournalEntry.date >= start_date)
    if end_date:
        query = query.filter(JournalEntry.date <= end_date)

    # Apply search
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            JournalEntry.description.ilike(f'%{search}%') |
            JournalEntry.reference.ilike(f'%{search}%') |
            JournalEntry.entry_number.ilike(f'%{search}%')
        )

    # Apply sorting
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')

    if hasattr(JournalEntry, sort_by):
        column = getattr(JournalEntry, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # Paginate results
    result = paginate_query(query, page, per_page)

    # Serialize journal entries with line items
    entries_data = []
    for entry in result['items']:
        entry_data = serialize_model(entry)
        entry_data['created_by'] = serialize_model(entry.creator) if entry.creator else None

        # Add line items
        line_items_data = []
        for line_item in entry.line_items:
            line_data = serialize_model(line_item)
            line_data['account'] = {
                'id': line_item.account.id,
                'code': line_item.account.code,
                'name': line_item.account.name
            } if line_item.account else None
            line_items_data.append(line_data)

        entry_data['line_items'] = line_items_data
        entries_data.append(entry_data)

    return api_response(data={
        'journal_entries': entries_data,
        'pagination': result['pagination']
    })

@journal_api_bp.route('/<int:entry_id>', methods=['GET'])
@require_api_key
def get_journal_entry(entry_id):
    """Get specific journal entry with line items"""
    entry = JournalEntry.query.filter_by(
        id=entry_id,
        organization_id=current_user.organization_id
    ).first()

    if not entry:
        return api_error('Journal entry not found', 404)

    entry_data = serialize_model(entry)
    entry_data['created_by'] = serialize_model(entry.creator) if entry.creator else None

    # Add line items with account details
    line_items_data = []
    for line_item in entry.line_items:
        line_data = serialize_model(line_item)
        line_data['account'] = {
            'id': line_item.account.id,
            'code': line_item.account.code,
            'name': line_item.account.name,
            'type': line_item.account.type.value if line_item.account.type else None
        } if line_item.account else None
        line_items_data.append(line_data)

    entry_data['line_items'] = line_items_data

    return api_response(data={'journal_entry': entry_data})

@journal_api_bp.route('', methods=['POST'])
@require_api_key
@validate_json_request(['date', 'description', 'line_items'])
def create_journal_entry():
    """Create new journal entry with line items"""
    data = request.get_json()

    try:
        # Parse date
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        # Generate entry number
        last_entry = JournalEntry.query.filter(
            JournalEntry.organization_id == current_user.organization_id,
            JournalEntry.entry_number.like('JE%')
        ).order_by(JournalEntry.id.desc()).first()

        if last_entry:
            last_num = int(last_entry.entry_number[2:])
            entry_number = f"JE{last_num + 1:06d}"
        else:
            entry_number = "JE000001"

        # Create journal entry
        journal_entry = JournalEntry(
            entry_number=entry_number,
            reference=data.get('reference', ''),
            date=entry_date,
            description=data['description'],
            source_type='manual',
            organization_id=current_user.organization_id,
            created_by=current_user.id
        )

        # Process line items
        line_items_data = data['line_items']
        if not line_items_data or len(line_items_data) < 2:
            return api_error('Journal entry must have at least 2 line items', 400)

        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')

        for line_data in line_items_data:
            account_id = line_data.get('account_id')
            debit = Decimal(str(line_data.get('debit', 0)))
            credit = Decimal(str(line_data.get('credit', 0)))
            description = line_data.get('description', '')

            # Validate account exists and belongs to organization
            account = Account.query.filter_by(
                id=account_id,
                organization_id=current_user.organization_id,
                is_active=True
            ).first()

            if not account:
                return api_error(f'Account {account_id} not found or inactive', 400)

            # Validate amounts
            if debit < 0 or credit < 0:
                return api_error('Debit and credit amounts cannot be negative', 400)

            if debit > 0 and credit > 0:
                return api_error('Line item cannot have both debit and credit amounts', 400)

            if debit == 0 and credit == 0:
                return api_error('Line item must have either debit or credit amount', 400)

            line_item = JournalLineItem(
                account_id=account_id,
                debit=debit,
                credit=credit,
                description=description
            )

            journal_entry.line_items.append(line_item)
            total_debit += debit
            total_credit += credit

        # Validate balanced entry
        if total_debit != total_credit:
            return api_error(
                f'Journal entry is not balanced. Debit total: {total_debit}, Credit total: {total_credit}',
                400
            )

        db.session.add(journal_entry)
        db.session.commit()

        # Return created entry
        entry_data = serialize_model(journal_entry)
        entry_data['created_by'] = serialize_model(journal_entry.creator)

        line_items_data = []
        for line_item in journal_entry.line_items:
            line_data = serialize_model(line_item)
            line_data['account'] = {
                'id': line_item.account.id,
                'code': line_item.account.code,
                'name': line_item.account.name
            }
            line_items_data.append(line_data)

        entry_data['line_items'] = line_items_data

        return api_response(
            data={'journal_entry': entry_data},
            message='Journal entry created successfully',
            status_code=201
        )

    except ValueError as e:
        return api_error(f'Invalid date format. Use YYYY-MM-DD', 400)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to create journal entry: {str(e)}', 500)

@journal_api_bp.route('/<int:entry_id>', methods=['PUT'])
@require_api_key
@validate_json_request(['date', 'description', 'line_items'])
def update_journal_entry(entry_id):
    """Update existing journal entry"""
    entry = JournalEntry.query.filter_by(
        id=entry_id,
        organization_id=current_user.organization_id
    ).first()

    if not entry:
        return api_error('Journal entry not found', 404)

    # Only allow updates for manual entries
    if entry.source_type != 'manual':
        return api_error('Only manual journal entries can be updated', 400)

    data = request.get_json()

    try:
        # Parse date
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        # Update basic fields
        entry.reference = data.get('reference', entry.reference)
        entry.date = entry_date
        entry.description = data['description']

        # Remove existing line items
        JournalLineItem.query.filter_by(journal_entry_id=entry_id).delete()

        # Process new line items
        line_items_data = data['line_items']
        if not line_items_data or len(line_items_data) < 2:
            return api_error('Journal entry must have at least 2 line items', 400)

        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')

        for line_data in line_items_data:
            account_id = line_data.get('account_id')
            debit = Decimal(str(line_data.get('debit', 0)))
            credit = Decimal(str(line_data.get('credit', 0)))
            description = line_data.get('description', '')

            # Validate account exists and belongs to organization
            account = Account.query.filter_by(
                id=account_id,
                organization_id=current_user.organization_id,
                is_active=True
            ).first()

            if not account:
                return api_error(f'Account {account_id} not found or inactive', 400)

            # Validate amounts
            if debit < 0 or credit < 0:
                return api_error('Debit and credit amounts cannot be negative', 400)

            if debit > 0 and credit > 0:
                return api_error('Line item cannot have both debit and credit amounts', 400)

            if debit == 0 and credit == 0:
                return api_error('Line item must have either debit or credit amount', 400)

            line_item = JournalLineItem(
                journal_entry_id=entry_id,
                account_id=account_id,
                debit=debit,
                credit=credit,
                description=description
            )

            db.session.add(line_item)
            total_debit += debit
            total_credit += credit

        # Validate balanced entry
        if total_debit != total_credit:
            return api_error(
                f'Journal entry is not balanced. Debit total: {total_debit}, Credit total: {total_credit}',
                400
            )

        db.session.commit()

        # Return updated entry
        entry_data = serialize_model(entry)
        entry_data['created_by'] = serialize_model(entry.creator) if entry.creator else None

        line_items_data = []
        for line_item in entry.line_items:
            line_data = serialize_model(line_item)
            line_data['account'] = {
                'id': line_item.account.id,
                'code': line_item.account.code,
                'name': line_item.account.name
            }
            line_items_data.append(line_data)

        entry_data['line_items'] = line_items_data

        return api_response(
            data={'journal_entry': entry_data},
            message='Journal entry updated successfully'
        )

    except ValueError as e:
        return api_error(f'Invalid date format. Use YYYY-MM-DD', 400)
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to update journal entry: {str(e)}', 500)

@journal_api_bp.route('/<int:entry_id>', methods=['DELETE'])
@require_api_key
def delete_journal_entry(entry_id):
    """Delete journal entry"""
    entry = JournalEntry.query.filter_by(
        id=entry_id,
        organization_id=current_user.organization_id
    ).first()

    if not entry:
        return api_error('Journal entry not found', 404)

    # Only allow deletion for manual entries
    if entry.source_type != 'manual':
        return api_error('Only manual journal entries can be deleted', 400)

    try:
        # Delete line items first
        JournalLineItem.query.filter_by(journal_entry_id=entry_id).delete()

        # Delete journal entry
        db.session.delete(entry)
        db.session.commit()

        return api_response(message='Journal entry deleted successfully')

    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to delete journal entry: {str(e)}', 500)