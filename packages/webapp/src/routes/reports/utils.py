"""
Shared utility functions for BigCapitalPy reports
"""

from datetime import date, timedelta
import calendar
import io
import csv
from flask import make_response
from decimal import Decimal


# get_date_range function has been moved to packages/webapp/src/utils/date_utils.py


def export_profit_loss_csv(report_data, report_period):
    """Export Profit & Loss report as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Profit & Loss Statement'])
    writer.writerow([f"{report_period['start_date']} to {report_period['end_date']}"])
    writer.writerow([])
    
    # Write income section
    writer.writerow(['INCOME'])
    for account in report_data['income_accounts']:
        writer.writerow([account['name'], str(account['balance'])])
    writer.writerow(['Total Income', str(report_data['total_income'])])
    writer.writerow([])
    
    # Write expense section
    writer.writerow(['EXPENSES'])
    for account in report_data['expense_accounts']:
        writer.writerow([account['name'], str(account['balance'])])
    writer.writerow(['Total Expenses', str(report_data['total_expenses'])])
    writer.writerow([])
    
    # Write net profit
    writer.writerow(['Net Profit', str(report_data['net_profit'])])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=profit_loss.csv'
    
    return response


def calculate_account_balance(account_id, start_date=None, end_date=None):
    """Calculate account balance for a given period"""
    from flask_login import current_user
    from packages.server.src.models import JournalEntry, JournalLineItem
    from packages.server.src.database import db
    from sqlalchemy import func
    
    query = db.session.query(func.sum(JournalLineItem.debit - JournalLineItem.credit)).filter(
        JournalLineItem.account_id == account_id
    ).join(JournalEntry).filter(
        JournalEntry.organization_id == current_user.organization_id
    )
    
    if start_date:
        query = query.filter(JournalEntry.date >= start_date)
    if end_date:
        query = query.filter(JournalEntry.date <= end_date)
    
    balance = query.scalar() or Decimal('0.00')
    return balance
