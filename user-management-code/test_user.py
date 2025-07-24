import unittest
from flask import url_for
from werkzeug.security import generate_password_hash
from datetime import datetime

from app import create_app, db
from app.models import User


class UserManagementTestCase(unittest.TestCase):
    """Test cases for user profile and settings management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        
        # Create a test user
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password_hash=generate_password_hash('testpassword123'),
            phone='(555) 123-4567',
            language='en',
            timezone='UTC',
            date_format='MM/DD/YYYY',
            currency_format='USD',
            email_notifications=True,
            dashboard_notifications=True,
            marketing_emails=False
        )
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login_user(self):
        """Helper method to log in the test user."""
        return self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword123'
        }, follow_redirects=True)
    
    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication."""
        response = self.client.get('/user/profile')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user."""
        self.login_user()
        response = self.client.get('/user/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Profile', response.data)
        self.assertIn(b'Test User', response.data)
        self.assertIn(b'test@example.com', response.data)
    
    def test_edit_profile_get(self):
        """Test GET request to edit profile page."""
        self.login_user()
        response = self.client.get('/user/profile/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Profile', response.data)
        self.assertIn(b'Test', response.data)  # First name should be pre-filled
    
    def test_edit_profile_post_valid(self):
        """Test valid profile update."""
        self.login_user()
        response = self.client.post('/user/profile/edit', data={
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'phone': '(555) 987-6543'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile updated successfully', response.data)
        
        # Verify database was updated
        user = User.query.filter_by(id=self.test_user.id).first()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')
        self.assertEqual(user.email, 'updated@example.com')
        self.assertEqual(user.phone, '(555) 987-6543')
    
    def test_edit_profile_duplicate_email(self):
        """Test updating profile with duplicate email."""
        # Create another user
        other_user = User(
            username='otheruser',
            email='other@example.com',
            first_name='Other',
            last_name='User',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(other_user)
        db.session.commit()
        
        self.login_user()
        response = self.client.post('/user/profile/edit', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'other@example.com',  # Duplicate email
            'phone': '(555) 123-4567'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email address is already in use', response.data)
    
    def test_change_password_get(self):
        """Test GET request to change password page."""
        self.login_user()
        response = self.client.get('/user/change-password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Change Password', response.data)
    
    def test_change_password_valid(self):
        """Test valid password change."""
        self.login_user()
        response = self.client.post('/user/change-password', data={
            'current_password': 'testpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password changed successfully', response.data)
        
        # Verify user can login with new password
        self.client.get('/auth/logout')
        login_response = self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'newpassword456'
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password."""
        self.login_user()
        response = self.client.post('/user/change-password', data={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Current password is incorrect', response.data)
    
    def test_settings_view(self):
        """Test settings view."""
        self.login_user()
        response = self.client.get('/user/settings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Settings &amp; Preferences', response.data)
        self.assertIn(b'Language &amp; Localization', response.data)
    
    def test_edit_settings_get(self):
        """Test GET request to edit settings page."""
        self.login_user()
        response = self.client.get('/user/settings/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Settings', response.data)
    
    def test_edit_settings_post_valid(self):
        """Test valid settings update."""
        self.login_user()
        response = self.client.post('/user/settings/edit', data={
            'language': 'es',
            'timezone': 'US/Pacific',
            'date_format': 'DD/MM/YYYY',
            'currency_format': 'EUR',
            'email_notifications': False,
            'dashboard_notifications': True,
            'marketing_emails': True
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Settings updated successfully', response.data)
        
        # Verify database was updated
        user = User.query.filter_by(id=self.test_user.id).first()
        self.assertEqual(user.language, 'es')
        self.assertEqual(user.timezone, 'US/Pacific')
        self.assertEqual(user.date_format, 'DD/MM/YYYY')
        self.assertEqual(user.currency_format, 'EUR')
        self.assertFalse(user.email_notifications)
        self.assertTrue(user.dashboard_notifications)
        self.assertTrue(user.marketing_emails)
    
    def test_user_model_methods(self):
        """Test User model helper methods."""
        user = self.test_user
        
        # Test full_name property
        self.assertEqual(user.full_name, 'Test User')
        
        # Test get_display_timezone method
        user.timezone = 'US/Eastern'
        self.assertEqual(user.get_display_timezone(), 'US/Eastern')
        
        # Test get_currency_symbol method
        user.currency_format = 'EUR'
        self.assertEqual(user.get_currency_symbol(), '€')
        
        user.currency_format = 'GBP'
        self.assertEqual(user.get_currency_symbol(), '£')
        
        user.currency_format = 'UNKNOWN'
        self.assertEqual(user.get_currency_symbol(), '$')  # Default
        
        # Test format_date method
        test_date = datetime(2023, 12, 25)
        
        user.date_format = 'MM/DD/YYYY'
        self.assertEqual(user.format_date(test_date), '12/25/2023')
        
        user.date_format = 'DD/MM/YYYY'
        self.assertEqual(user.format_date(test_date), '25/12/2023')
        
        user.date_format = 'YYYY-MM-DD'
        self.assertEqual(user.format_date(test_date), '2023-12-25')
        
        # Test with None date
        self.assertEqual(user.format_date(None), '')


class UserFormsTestCase(unittest.TestCase):
    """Test cases for user forms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_profile_form_validation(self):
        """Test ProfileForm validation."""
        from app.user.forms import ProfileForm
        
        # Test valid form
        with self.app.test_request_context():
            form = ProfileForm(data={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'phone': '(555) 123-4567'
            })
            self.assertTrue(form.validate())
        
        # Test missing required fields
        with self.app.test_request_context():
            form = ProfileForm(data={
                'first_name': '',
                'last_name': 'Doe',
                'email': 'john@example.com'
            })
            self.assertFalse(form.validate())
            self.assertIn('This field is required.', form.first_name.errors)
    
    def test_password_form_validation(self):
        """Test PasswordForm validation."""
        from app.user.forms import PasswordForm
        
        # Test valid form
        with self.app.test_request_context():
            form = PasswordForm(data={
                'current_password': 'oldpassword123',
                'new_password': 'newpassword456',
                'confirm_password': 'newpassword456'
            })
            self.assertTrue(form.validate())
        
        # Test password mismatch
        with self.app.test_request_context():
            form = PasswordForm(data={
                'current_password': 'oldpassword123',
                'new_password': 'newpassword456',
                'confirm_password': 'differentpassword'
            })
            self.assertFalse(form.validate())
            self.assertIn('Passwords must match', form.confirm_password.errors)
    
    def test_settings_form_validation(self):
        """Test SettingsForm validation."""
        from app.user.forms import SettingsForm
        
        # Test valid form
        with self.app.test_request_context():
            form = SettingsForm(data={
                'language': 'en',
                'timezone': 'UTC',
                'date_format': 'MM/DD/YYYY',
                'currency_format': 'USD',
                'email_notifications': True,
                'dashboard_notifications': True,
                'marketing_emails': False
            })
            self.assertTrue(form.validate())


if __name__ == '__main__':
    unittest.main()