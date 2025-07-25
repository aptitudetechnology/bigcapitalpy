# BigCapitalPy Financial Data Structure & Query Report

## 1. Database Schema

- **Accounts**: The `Account` model (`accounts` table) stores all accounts. It has a `type` field (`db.Enum(AccountType)`) to distinguish account types (e.g., income, expense, asset, liability).
- **Transactions/Journal Entries**: The `JournalEntry` model (`journal_entries` table) stores each journal entry. Each entry has many `JournalLineItem` records (`journal_line_items` table), which represent debits/credits to specific accounts.
- **Relationships**:
  - `Account` has a self-referencing `parent_id` for hierarchy.
  - `JournalLineItem` has an `account_id` foreign key to `Account`.
  - `JournalEntry` has many `JournalLineItem`s via `line_items` relationship.
- **Account Types**: The `AccountType` enum distinguishes income, expense, etc.

---

## 2. Data Retrieval

- **Income/Expense Accounts**: Query `Account` where `type == AccountType.INCOME` or `type == AccountType.EXPENSE`.
- **Balances for Date Range**: Sum the amounts from `JournalLineItem` for each account, filtered by `JournalEntry.date` between your start and end dates.
- **Sample SQLAlchemy Query**:

```python
from packages.server.src.models import db, Account, AccountType, JournalEntry, JournalLineItem
from sqlalchemy import func

# Example: Get balances for all income accounts in a date range
income_accounts = Account.query.filter_by(type=AccountType.INCOME).all()
start_date, end_date = ... # your date range

results = (
    db.session.query(
        Account.id,
        Account.name,
        func.coalesce(func.sum(JournalLineItem.amount), 0).label('balance')
    )
    .join(JournalLineItem, JournalLineItem.account_id == Account.id)
    .join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
    .filter(Account.type == AccountType.INCOME)
    .filter(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
    .group_by(Account.id)
    .all()
)
```

---

## 3. Current Implementation

- **Balance Calculation**: There is no explicit `get_balance` method shown, but you can use the above query pattern.
- **Models/Services**: The models are in `packages/server/src/models/__init__.py`. If you have a `reporting` or `services` module, it may contain reusable functions.
- **Best Practice**: Use SQLAlchemy queries as above, filtering by account type and date range.

---

## 4. Sample Query for Profit & Loss

```python
from packages.server.src.models import db, Account, AccountType, JournalEntry, JournalLineItem
from sqlalchemy import func

def get_profit_loss_data(start_date, end_date):
    # Income
    income = (
        db.session.query(
            Account.id,
            Account.name,
            func.coalesce(func.sum(JournalLineItem.amount), 0).label('balance')
        )
        .join(JournalLineItem, JournalLineItem.account_id == Account.id)
        .join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
        .filter(Account.type == AccountType.INCOME)
        .filter(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
        .group_by(Account.id)
        .all()
    )
    # Expense
    expense = (
        db.session.query(
            Account.id,
            Account.name,
            func.coalesce(func.sum(JournalLineItem.amount), 0).label('balance')
        )
        .join(JournalLineItem, JournalLineItem.account_id == Account.id)
        .join(JournalEntry, JournalLineItem.journal_entry_id == JournalEntry.id)
        .filter(Account.type == AccountType.EXPENSE)
        .filter(JournalEntry.date >= start_date, JournalEntry.date <= end_date)
        .group_by(Account.id)
        .all()
    )
    return {'income': income, 'expense': expense}
```
- This returns all income and expense accounts with their balances for the given period.
- Accounts with zero balances will still appear if you use a left outer join or handle missing data.

---

**Summary:**
- Accounts are in the `accounts` table, transactions in `journal_entries` and `journal_line_items`.
- Use account type to distinguish income/expense.
- Query balances by summing line items for each account in the date range.
- Use the provided sample query to implement your `generate_profit_loss_data()` function.

---
