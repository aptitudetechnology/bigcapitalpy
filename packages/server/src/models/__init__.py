"""
SQLAlchemy Models for BigCapitalPy Accounting System
"""

from datetime import datetime, date
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
import enum

from packages.server.src.database import db

# Enums for various fields
class AccountType(enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"

class TransactionType(enum.Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    PAYMENT = "payment"
    RECEIPT = "receipt"
    JOURNAL = "journal"

class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentMethod(enum.Enum):
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    OTHER = "other"

# Core Models
class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    legal_name = db.Column(db.String(255))
    tax_number = db.Column(db.String(100))
    registration_number = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    currency = db.Column(db.String(3), default='USD')
    fiscal_year_start = db.Column(db.String(5), default='01-01')  # MM-DD format
    timezone = db.Column(db.String(50), default='UTC')
    logo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='organization', lazy=True)
    accounts = db.relationship('Account', backref='organization', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    avatar_url = db.Column(db.String(500))
    role = db.Column(db.String(50), default='user')  # admin, accountant, user
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(AccountType), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    opening_balance = db.Column(db.Numeric(15, 2), default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Relationships
    children = db.relationship('Account', backref=db.backref('parent', remote_side=[id]))
    
    def __repr__(self):
        return f'<Account {self.code}: {self.name}>'

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    
    # Billing Address
    billing_address = db.Column(db.Text)
    billing_city = db.Column(db.String(100))
    billing_state = db.Column(db.String(100))
    billing_postal_code = db.Column(db.String(20))
    billing_country = db.Column(db.String(100))
    
    # Shipping Address
    shipping_address = db.Column(db.Text)
    shipping_city = db.Column(db.String(100))
    shipping_state = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(20))
    shipping_country = db.Column(db.String(100))
    
    # Financial Info
    currency = db.Column(db.String(3), default='USD')
    opening_balance = db.Column(db.Numeric(15, 2), default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    
    # Settings
    tax_number = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    def __repr__(self):
        return f'<Customer {self.display_name}>'

class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Financial Info
    currency = db.Column(db.String(3), default='USD')
    opening_balance = db.Column(db.Numeric(15, 2), default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    
    # Settings
    tax_number = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    def __repr__(self):
        return f'<Vendor {self.display_name}>'

class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    
    # Pricing
    sell_price = db.Column(db.Numeric(15, 2), default=0)
    cost_price = db.Column(db.Numeric(15, 2), default=0)
    
    # Inventory
    quantity_on_hand = db.Column(db.Numeric(15, 2), default=0)
    reorder_level = db.Column(db.Numeric(15, 2), default=0)
    
    # Settings
    type = db.Column(db.String(50), default='inventory')  # inventory, service, non-inventory
    category = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    weight = db.Column(db.Numeric(10, 2))
    dimensions = db.Column(db.String(100))
    
    # Accounting
    income_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    expense_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    inventory_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Relationships
    income_account = db.relationship('Account', foreign_keys=[income_account_id])
    expense_account = db.relationship('Account', foreign_keys=[expense_account_id])
    inventory_account = db.relationship('Account', foreign_keys=[inventory_account_id])
    
    def __repr__(self):
        return f'<Item {self.name}>'

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), nullable=False, unique=True)
    reference = db.Column(db.String(100))
    
    # Dates
    invoice_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    
    # Customer Info
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Financial
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    total = db.Column(db.Numeric(15, 2), default=0)
    paid_amount = db.Column(db.Numeric(15, 2), default=0)
    balance = db.Column(db.Numeric(15, 2), default=0)
    
    # Settings
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    terms = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Relationships
    customer = db.relationship('Customer', backref='invoices')
    line_items = db.relationship('InvoiceLineItem', backref='invoice', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

class InvoiceLineItem(db.Model):
    __tablename__ = 'invoice_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    
    # Product details
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Numeric(15, 2), nullable=False, default=1)
    rate = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    amount = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    
    # Tax
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Relationships
    item = db.relationship('Item')

# Journal and Transaction Models
class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(50), nullable=False)
    reference = db.Column(db.String(100))
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.Text)
    
    # Totals (for validation)
    debit_total = db.Column(db.Numeric(15, 2), default=0)
    credit_total = db.Column(db.Numeric(15, 2), default=0)
    
    # Source document reference
    source_type = db.Column(db.String(50))  # invoice, bill, payment, etc.
    source_id = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    line_items = db.relationship('JournalLineItem', backref='journal_entry', cascade='all, delete-orphan')
    creator = db.relationship('User')

class JournalLineItem(db.Model):
    __tablename__ = 'journal_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    
    description = db.Column(db.String(500))
    debit = db.Column(db.Numeric(15, 2), default=0)
    credit = db.Column(db.Numeric(15, 2), default=0)
    
    # Contact reference (customer/vendor)
    contact_type = db.Column(db.String(50))  # customer, vendor
    contact_id = db.Column(db.Integer)
    
    # Relationships
    account = db.relationship('Account')

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Payment details
    reference = db.Column(db.String(255))
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False, default=PaymentMethod.CASH)
    notes = db.Column(db.Text)
    
    # Bank details (for bank transfers/checks)
    bank_name = db.Column(db.String(255))
    check_number = db.Column(db.String(100))
    
    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    deposit_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer')
    deposit_account = db.relationship('Account')
    creator = db.relationship('User')
    payment_allocations = db.relationship('PaymentAllocation', backref='payment', cascade='all, delete-orphan')

class PaymentAllocation(db.Model):
    __tablename__ = 'payment_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    allocated_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = db.relationship('Invoice')

class BankTransaction(db.Model):
    """Bank transactions imported from CSV/bank feeds"""
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    reference = db.Column(db.String(100))
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # Positive for deposits, negative for withdrawals
    balance = db.Column(db.Numeric(15, 2))  # Running balance after this transaction
    bank_transaction_id = db.Column(db.String(100))  # Bank's unique identifier
    transaction_type = db.Column(db.String(50))  # DEBIT, CREDIT, etc.
    status = db.Column(db.String(20), default='unmatched')  # unmatched, matched, reconciled
    organization_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = db.relationship('Account', backref='bank_transactions')
    matches = db.relationship('ReconciliationMatch', backref='bank_transaction', cascade='all, delete-orphan')

class BankReconciliation(db.Model):
    """Bank reconciliation sessions"""
    __tablename__ = 'bank_reconciliations'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    reconciliation_date = db.Column(db.Date, nullable=False)
    statement_ending_date = db.Column(db.Date, nullable=False)
    statement_ending_balance = db.Column(db.Numeric(15, 2), nullable=False)
    book_ending_balance = db.Column(db.Numeric(15, 2), nullable=False)
    difference = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, discarded
    notes = db.Column(db.Text)
    organization_id = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = db.relationship('Account', backref='reconciliations')
    creator = db.relationship('User', backref='reconciliations')
    matches = db.relationship('ReconciliationMatch', backref='reconciliation', cascade='all, delete-orphan')

class ReconciliationMatch(db.Model):
    """Matches between bank transactions and journal entries"""
    __tablename__ = 'reconciliation_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    reconciliation_id = db.Column(db.Integer, db.ForeignKey('bank_reconciliations.id'), nullable=False)
    bank_transaction_id = db.Column(db.Integer, db.ForeignKey('bank_transactions.id'))
    journal_line_item_id = db.Column(db.Integer, db.ForeignKey('journal_line_items.id'))
    match_type = db.Column(db.String(20), nullable=False)  # automatic, manual, created
    confidence_score = db.Column(db.Float, default=0.0)  # For automatic matching
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships  
    journal_line_item = db.relationship('JournalLineItem', backref='reconciliation_matches')
