from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
import pytz


class ProfileForm(FlaskForm):
    """Form for editing user profile information."""
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    
    email = EmailField('Email Address', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=20)
    ])


class PasswordForm(FlaskForm):
    """Form for changing user password."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])


class SettingsForm(FlaskForm):
    """Form for editing user settings and preferences."""
    
    # Language and localization
    language = SelectField('Language', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ar', 'Arabic'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ko', 'Korean')
    ], default='en')
    
    # Timezone selection (populated dynamically)
    timezone = SelectField('Timezone', choices=[], default='UTC')
    
    # Date and currency formatting
    date_format = SelectField('Date Format', choices=[
        ('MM/DD/YYYY', 'MM/DD/YYYY (US)'),
        ('DD/MM/YYYY', 'DD/MM/YYYY (European)'),
        ('YYYY-MM-DD', 'YYYY-MM-DD (ISO)'),
        ('DD-MM-YYYY', 'DD-MM-YYYY'),
        ('MM-DD-YYYY', 'MM-DD-YYYY')
    ], default='MM/DD/YYYY')
    
    currency_format = SelectField('Currency Format', choices=[
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('AUD', 'Australian Dollar (A$)'),
        ('CHF', 'Swiss Franc (CHF)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('INR', 'Indian Rupee (₹)'),
        ('BRL', 'Brazilian Real (R$)')
    ], default='USD')
    
    # Notification preferences
    email_notifications = BooleanField('Email Notifications', default=True)
    dashboard_notifications = BooleanField('Dashboard Notifications', default=True)
    marketing_emails = BooleanField('Marketing Emails', default=False)
    
    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        # Populate timezone choices
        self.timezone.choices = self._get_timezone_choices()
    
    def _get_timezone_choices(self):
        """Get sorted list of timezone choices."""
        common_timezones = [
            ('UTC', 'UTC'),
            ('US/Eastern', 'US/Eastern'),
            ('US/Central', 'US/Central'),
            ('US/Mountain', 'US/Mountain'),
            ('US/Pacific', 'US/Pacific'),
            ('Europe/London', 'Europe/London'),
            ('Europe/Paris', 'Europe/Paris'),
            ('Europe/Berlin', 'Europe/Berlin'),
            ('Asia/Tokyo', 'Asia/Tokyo'),
            ('Asia/Shanghai', 'Asia/Shanghai'),
            ('Asia/Kolkata', 'Asia/Kolkata'),
            ('Australia/Sydney', 'Australia/Sydney'),
        ]
        
        # Add all other timezones
        all_timezones = [(tz, tz) for tz in sorted(pytz.all_timezones) 
                        if (tz, tz) not in common_timezones]
        
        return common_timezones + [('', '--- Other Timezones ---')] + all_timezones