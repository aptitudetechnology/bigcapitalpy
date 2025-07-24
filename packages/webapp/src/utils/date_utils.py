"""
General date utility functions for BigCapitalPy.
"""

from datetime import date, timedelta
import calendar
from datetime import datetime # Import datetime here as it's used in the function


def get_date_range(period=None, start_date=None, end_date=None):
    """Get date range based on period or custom dates"""
    today = date.today()
    
    if period == 'this_month':
        start_date = today.replace(day=1)
        end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    elif period == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1)
        end_date = last_month.replace(day=calendar.monthrange(last_month.year, last_month.month)[1])
    elif period == 'this_quarter':
        quarter = (today.month - 1) // 3 + 1
        start_date = date(today.year, 3 * quarter - 2, 1)
        end_date = date(today.year, 3 * quarter, calendar.monthrange(today.year, 3 * quarter)[1])
    elif period == 'last_quarter':
        quarter = (today.month - 1) // 3 + 1
        if quarter == 1:
            quarter = 4
            year = today.year - 1
        else:
            quarter -= 1
            year = today.year
        start_date = date(year, 3 * quarter - 2, 1)
        end_date = date(year, 3 * quarter, calendar.monthrange(year, 3 * quarter)[1])
    elif period == 'this_year':
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 12, 31)
    elif period == 'last_year':
        start_date = date(today.year - 1, 1, 1)
        end_date = date(today.year - 1, 12, 31)
    else:
        # Custom period or default to current month
        if start_date:
            if isinstance(start_date, str):
                # Import datetime here as it's only needed for string conversion
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = today.replace(day=1)
        
        if end_date:
            if isinstance(end_date, str):
                # Import datetime here as it's only needed for string conversion
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    
    return start_date, end_date
