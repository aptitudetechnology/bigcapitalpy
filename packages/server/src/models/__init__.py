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

class TaxType(enum.Enum):
    """Tax type enumeration"""
    GST_STANDARD = "gst_standard"
    GST_FREE = "gst_free"
    EXPORT = "export"
    INPUT_TAXED = "input_taxed"
    CAPITAL_ACQUISITION = "capital_acquisition"

class TaxCode(db.Model):
    __tablename__ = 'tax_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Tax configuration
    tax_type = db.Column(db.Enum(TaxType), nullable=False, default=TaxType.GST_STANDARD)
    rate = db.Column(db.Numeric(5, 2), default=0)  # Tax rate as percentage (e.g., 10.00 for 10%)
    
    # Account associations
    tax_payable_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    tax_receivable_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    is_system = db.Column(db.Boolean, default=False)  # System tax codes cannot be deleted
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Relationships
    tax_payable_account = db.relationship('Account', foreign_keys=[tax_payable_account_id])
    tax_receivable_account = db.relationship('Account', foreign_keys=[tax_receivable_account_id])
    
    def __repr__(self):
        return f'<TaxCode {self.code}: {self.name}>'

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
    tax_code_id = db.Column(db.Integer, db.ForeignKey('tax_codes.id'))
    
    # Relationships
    item = db.relationship('Item')
    tax_code = db.relationship('TaxCode')

# Journal and Transaction Models
class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(50), nullable=False)
    reference = db.Column(db.String(100))
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.Text)
    
    # Totals (for validation - debits must equal credits)
    debit_total = db.Column(db.Numeric(15, 2), default=0)
    credit_total = db.Column(db.Numeric(15, 2), default=0)
    
    # Source document reference for audit trail
    source_type = db.Column(db.String(50))  # invoice, bill, payment, manual, etc.
    source_id = db.Column(db.Integer)
    
    # Status and approval workflow
    status = db.Column(db.String(20), default='draft')  # draft, posted, reversed
    posted_at = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    line_items = db.relationship('JournalLineItem', backref='journal_entry', cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by])
    poster = db.relationship('User', foreign_keys=[posted_by])
    
    @property
    def is_balanced(self):
        """Check if journal entry is balanced (debits = credits)"""
        return abs(self.debit_total - self.credit_total) < 0.01
    
    def __repr__(self):
        return f'<JournalEntry {self.entry_number}: {self.description[:50] if self.description else ""}>'

class JournalLineItem(db.Model):
    __tablename__ = 'journal_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    
    # Line item details
    description = db.Column(db.String(500))
    debit = db.Column(db.Numeric(15, 2), default=0)
    credit = db.Column(db.Numeric(15, 2), default=0)
    
    # Tax information
    tax_code_id = db.Column(db.Integer, db.ForeignKey('tax_codes.id'))
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Contact reference (for customer/vendor specific transactions)
    contact_type = db.Column(db.String(50))  # customer, vendor
    contact_id = db.Column(db.Integer)
    
    # Additional metadata
    line_number = db.Column(db.Integer, default=1)  # Order within the journal entry
    
    # Relationships
    account = db.relationship('Account')
    tax_code = db.relationship('TaxCode')
    
    @property
    def amount(self):
        """Return the non-zero amount (either debit or credit)"""
        return self.debit if self.debit > 0 else self.credit
    
    def __repr__(self):
        amount = self.debit if self.debit > 0 else -self.credit
        return f'<JournalLineItem {self.account.code if self.account else "N/A"}: {amount}>'

# Australian BAS Report Model
class BASReport(db.Model):
    __tablename__ = 'bas_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_number = db.Column(db.String(50), nullable=False)
    
    # Report Period
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    reporting_period = db.Column(db.String(20), nullable=False)  # quarterly, monthly
    
    # GST Calculations
    g1_total_sales = db.Column(db.Numeric(15, 2), default=0)  # Total sales (including GST)
    g2_export_sales = db.Column(db.Numeric(15, 2), default=0)  # Export sales
    g3_other_gst_free_sales = db.Column(db.Numeric(15, 2), default=0)  # Other GST-free sales
    g4_input_taxed_sales = db.Column(db.Numeric(15, 2), default=0)  # Input taxed sales
    g10_capital_sales = db.Column(db.Numeric(15, 2), default=0)  # Capital sales
    g11_non_capital_sales = db.Column(db.Numeric(15, 2), default=0)  # Non-capital sales
    
    # GST on Sales
    g1a_gst_on_sales = db.Column(db.Numeric(15, 2), default=0)  # GST on sales
    g10a_gst_on_capital_sales = db.Column(db.Numeric(15, 2), default=0)  # GST on capital sales
    g11a_gst_on_non_capital_sales = db.Column(db.Numeric(15, 2), default=0)  # GST on non-capital sales
    
    # GST on Purchases
    g7_total_purchases = db.Column(db.Numeric(15, 2), default=0)  # Total purchases (including GST)
    g18_capital_purchases = db.Column(db.Numeric(15, 2), default=0)  # Capital purchases
    g19_non_capital_purchases = db.Column(db.Numeric(15, 2), default=0)  # Non-capital purchases
    g7a_gst_on_purchases = db.Column(db.Numeric(15, 2), default=0)  # GST on purchases
    g18a_gst_on_capital_purchases = db.Column(db.Numeric(15, 2), default=0)  # GST on capital purchases
    g19a_gst_on_non_capital_purchases = db.Column(db.Numeric(15, 2), default=0)  # GST on non-capital purchases
    
    # Calculation Fields
    g1b_total_gst_on_sales = db.Column(db.Numeric(15, 2), default=0)  # Total GST on sales (1A + 10A + 11A)
    g7b_total_gst_on_purchases = db.Column(db.Numeric(15, 2), default=0)  # Total GST on purchases (7A + 18A + 19A)
    g9_gst_payable_refund = db.Column(db.Numeric(15, 2), default=0)  # Net GST (1B - 7B)
    
    # Wine Equalisation Tax (if applicable)
    g5a_wine_sales_liable = db.Column(db.Numeric(15, 2), default=0)
    g5b_wine_tax_payable = db.Column(db.Numeric(15, 2), default=0)
    g6a_wine_purchases_liable = db.Column(db.Numeric(15, 2), default=0)
    g6b_wine_tax_credits = db.Column(db.Numeric(15, 2), default=0)
    
    # Luxury Car Tax (if applicable)
    g12_luxury_car_sales = db.Column(db.Numeric(15, 2), default=0)
    g12a_luxury_car_tax = db.Column(db.Numeric(15, 2), default=0)
    g13_luxury_car_purchases = db.Column(db.Numeric(15, 2), default=0)
    g13a_luxury_car_tax_credits = db.Column(db.Numeric(15, 2), default=0)
    
    # Fuel Tax Credits (if applicable)
    g14_fuel_tax_credits = db.Column(db.Numeric(15, 2), default=0)
    
    # PAYG Withholding
    g20_total_salary_wages = db.Column(db.Numeric(15, 2), default=0)
    g21_payg_withholding = db.Column(db.Numeric(15, 2), default=0)
    
    # PAYG Instalments
    g22_payg_instalment_income = db.Column(db.Numeric(15, 2), default=0)
    g23_payg_instalment_amount = db.Column(db.Numeric(15, 2), default=0)
    g24_payg_instalment_credit = db.Column(db.Numeric(15, 2), default=0)
    
    # Final Calculations
    g25_total_tax_payable = db.Column(db.Numeric(15, 2), default=0)  # Total tax payable
    g26_total_credits = db.Column(db.Numeric(15, 2), default=0)  # Total credits
    g27_net_amount = db.Column(db.Numeric(15, 2), default=0)  # Net amount (payable/refund)
    
    # Report Status and Metadata
    status = db.Column(db.String(20), default='draft')  # draft, lodged, amended
    lodged_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    abn = db.Column(db.String(20))  # Australian Business Number
    
    # Additional Information
    notes = db.Column(db.Text)
    prepared_by = db.Column(db.String(255))
    reviewed_by = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lodged_at = db.Column(db.DateTime)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lodged_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    organization = db.relationship('Organization')
    creator = db.relationship('User', foreign_keys=[created_by])
    lodger = db.relationship('User', foreign_keys=[lodged_by])
    
    @property
    def is_quarterly(self):
        """Check if this is a quarterly BAS report"""
        return self.reporting_period == 'quarterly'
    
    @property
    def is_monthly(self):
        """Check if this is a monthly BAS report"""
        return self.reporting_period == 'monthly'
    
    @property
    def period_description(self):
        """Get a human-readable description of the reporting period"""
        if self.is_quarterly:
            quarter = ((self.period_start.month - 1) // 3) + 1
            return f"Q{quarter} {self.period_start.year}"
        else:
            return f"{self.period_start.strftime('%B %Y')}"
    
    def calculate_totals(self):
        """Calculate derived fields from the individual components"""
        # Total GST on sales (1B = 1A + 10A + 11A)
        self.g1b_total_gst_on_sales = (
            (self.g1a_gst_on_sales or 0) + 
            (self.g10a_gst_on_capital_sales or 0) + 
            (self.g11a_gst_on_non_capital_sales or 0)
        )
        
        # Total GST on purchases (7B = 7A + 18A + 19A)
        self.g7b_total_gst_on_purchases = (
            (self.g7a_gst_on_purchases or 0) + 
            (self.g18a_gst_on_capital_purchases or 0) + 
            (self.g19a_gst_on_non_capital_purchases or 0)
        )
        
        # Net GST (G9 = 1B - 7B)
        self.g9_gst_payable_refund = self.g1b_total_gst_on_sales - self.g7b_total_gst_on_purchases
        
        # Calculate total tax payable (G25)
        wine_tax = (self.g5b_wine_tax_payable or 0) - (self.g6b_wine_tax_credits or 0)
        luxury_car_tax = (self.g12a_luxury_car_tax or 0) - (self.g13a_luxury_car_tax_credits or 0)
        
        self.g25_total_tax_payable = (
            self.g9_gst_payable_refund + 
            wine_tax + 
            luxury_car_tax + 
            (self.g21_payg_withholding or 0) + 
            (self.g23_payg_instalment_amount or 0)
        )
        
        # Calculate total credits (G26)
        self.g26_total_credits = (
            (self.g14_fuel_tax_credits or 0) + 
            (self.g24_payg_instalment_credit or 0)
        )
        
        # Net amount (G27 = G25 - G26)
        self.g27_net_amount = self.g25_total_tax_payable - self.g26_total_credits
    
    def __repr__(self):
        return f'<BASReport {self.report_number}: {self.period_description}>'


class BankTransaction(db.Model):
    """Model for imported bank transactions used in reconciliation"""
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    reference = db.Column(db.String(100))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    balance = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(20), default='unmatched')  # unmatched, matched, reconciled
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = db.relationship('Account', backref='bank_transactions')
    organization = db.relationship('Organization', backref='bank_transactions')
    
    def __repr__(self):
        return f'<BankTransaction {self.transaction_date}: {self.description} - {self.amount}>'


class BankReconciliation(db.Model):
    """Model for bank reconciliation sessions"""
    __tablename__ = 'bank_reconciliations'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    reconciliation_date = db.Column(db.Date, nullable=False)
    statement_ending_date = db.Column(db.Date, nullable=False)
    statement_ending_balance = db.Column(db.Numeric(15, 2), nullable=False)
    book_ending_balance = db.Column(db.Numeric(15, 2), nullable=False)
    difference = db.Column(db.Numeric(15, 2), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = db.relationship('Account', backref='reconciliations')
    organization = db.relationship('Organization', backref='reconciliations')
    creator = db.relationship('User', backref='reconciliations')
    
    def __repr__(self):
        return f'<BankReconciliation {self.reconciliation_date}: Account {self.account_id}>'

class ReconciliationMatch(db.Model):
    """Model for matching bank transactions to journal entries during reconciliation"""
    __tablename__ = 'reconciliation_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    reconciliation_id = db.Column(db.Integer, db.ForeignKey('bank_reconciliations.id'), nullable=False)
    bank_transaction_id = db.Column(db.Integer, db.ForeignKey('bank_transactions.id'), nullable=True)
    journal_line_item_id = db.Column(db.Integer, db.ForeignKey('journal_line_items.id'), nullable=True)
    match_type = db.Column(db.String(20), default='manual')  # manual, automatic
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reconciliation = db.relationship('BankReconciliation', backref='matches')
    bank_transaction = db.relationship('BankTransaction', backref='matches')
    journal_line_item = db.relationship('JournalLineItem', backref='reconciliation_matches')
    
    def __repr__(self):
        return f'<ReconciliationMatch {self.id}: {self.match_type}>'


# Payment Models
class Payment(db.Model):
    """Model for payments received from customers"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), nullable=False, unique=True)
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Bank/Check details
    bank_name = db.Column(db.String(255))
    check_number = db.Column(db.String(50))
    
    # Relationships
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    deposit_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='payments')
    deposit_account = db.relationship('Account', backref='payments')
    organization = db.relationship('Organization', backref='payments')
    creator = db.relationship('User', backref='payments')
    
    def __repr__(self):
        return f'<Payment {self.payment_number}: {self.amount}>'

class PaymentAllocation(db.Model):
    """Model for allocating payments to specific invoices"""
    __tablename__ = 'payment_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    allocated_amount = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payment = db.relationship('Payment', backref='allocations')
    invoice = db.relationship('Invoice', backref='payment_allocations')
    
    def __repr__(self):
        return f'<PaymentAllocation {self.payment_id} -> {self.invoice_id}: {self.allocated_amount}>'
