# Add these fields to your existing User model
# This shows the additional columns needed for user settings

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model with profile and settings fields."""
    
    __tablename__ = 'users'
    
    # Existing fields (keep your current implementation)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Profile fields
    phone = db.Column(db.String(20), nullable=True)
    
    # Settings fields (add these to your existing model)
    language = db.Column(db.String(10), default='en')
    timezone = db.Column(db.String(50), default='UTC')
    date_format = db.Column(db.String(20), default='MM/DD/YYYY')
    currency_format = db.Column(db.String(10), default='USD')
    
    # Notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    dashboard_notifications = db.Column(db.Boolean, default=True)
    marketing_emails = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        """Return full name of user."""
        return f"{self.first_name} {self.last_name}"
    
    def get_display_timezone(self):
        """Get user-friendly timezone display."""
        return self.timezone.replace('_', ' ')
    
    def get_currency_symbol(self):
        """Get currency symbol for user's preferred currency."""
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'CAD': 'C$',
            'AUD': 'A$',
            'CHF': 'CHF',
            'CNY': '¥',
            'INR': '₹',
            'BRL': 'R$'
        }
        return currency_symbols.get(self.currency_format, '$')
    
    def format_date(self, date_obj):
        """Format date according to user preference."""
        if not date_obj:
            return ''
        
        format_map = {
            'MM/DD/YYYY': '%m/%d/%Y',
            'DD/MM/YYYY': '%d/%m/%Y',
            'YYYY-MM-DD': '%Y-%m-%d',
            'DD-MM-YYYY': '%d-%m-%Y',
            'MM-DD-YYYY': '%m-%d-%Y'
        }
        
        format_str = format_map.get(self.date_format, '%m/%d/%Y')
        return date_obj.strftime(format_str)