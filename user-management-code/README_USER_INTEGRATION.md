# User Management Integration Guide

This guide explains how to integrate the user profile and settings management functionality into your BigCapital Flask application.

## 1. File Structure

Add the following files to your project:

```
app/
├── user/
│   ├── __init__.py
│   ├── routes.py
│   └── forms.py
├── models/
│   └── user.py (update existing)
├── templates/
│   └── user/
│       ├── profile.html
│       ├── edit_profile.html
│       ├── change_password.html
│       ├── settings.html
│       └── edit_settings.html
├── templates/includes/
│   └── navbar.html (update existing)
├── tests/
│   └── test_user.py
└── migrations/
    └── add_user_settings.py
```

## 2. Register the Blueprint

In your main application factory (`app/__init__.py`), register the user blueprint:

```python
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    # ... other extensions
    
    # Register blueprints
    from .user import user_bp
    app.register_blueprint(user_bp)
    
    # ... register other blueprints
    
    return app
```

## 3. Update Your User Model

Add the new fields to your existing User model in `app/models/user.py`:

```python
class User(UserMixin, db.Model):
    # ... existing fields ...
    
    # Profile fields
    phone = db.Column(db.String(20), nullable=True)
    
    # Settings fields
    language = db.Column(db.String(10), default='en')
    timezone = db.Column(db.String(50), default='UTC')
    date_format = db.Column(db.String(20), default='MM/DD/YYYY')
    currency_format = db.Column(db.String(10), default='USD')
    
    # Notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    dashboard_notifications = db.Column(db.Boolean, default=True)
    marketing_emails = db.Column(db.Boolean, default=False)
    
    # Add the helper methods from user_models_update.py
```

## 4. Run Database Migration

1. Create and run the migration:

```bash
# If using Flask-Migrate
flask db migrate -m "Add user settings and profile fields"
flask db upgrade

# Or run the custom migration script
python migrations/add_user_settings.py
```

## 5. Update Your Navigation

Update your navbar template to include the user menu dropdown (see `navbar_update.html`).

## 6. Install Required Dependencies

Make sure you have these packages in your `requirements.txt`:

```
pytz>=2023.3  # For timezone support
```

Install with:
```bash
pip install pytz
```

## 7. Configuration

Add any necessary configuration to your `config.py`:

```python
class Config:
    # ... existing config ...
    
    # User settings defaults
    DEFAULT_TIMEZONE = 'UTC'
    DEFAULT_LANGUAGE = 'en'
    DEFAULT_DATE_FORMAT = 'MM/DD/YYYY'
    DEFAULT_CURRENCY = 'USD'
```

## 8. Template Inheritance

Make sure your base template (`templates/base.html`) includes:

1. Bootstrap CSS and JS for styling
2. Font Awesome for icons
3. Flash message display
4. Blocks for `title`, `content`, and `scripts`

Example base template structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}BigCapital{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    {% include 'includes/navbar.html' %}
    
    <main class="py-4">
        <!-- Flash messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="container">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

## 9. Testing

Run the tests to ensure everything works correctly:

```bash
python -m pytest tests/test_user.py -v
```

## 10. URL Routes

The following routes will be available after integration:

- `/user/profile` - View user profile
- `/user/profile/edit` - Edit user profile
- `/user/change-password` - Change password
- `/user/settings` - View user settings
- `/user/settings/edit` - Edit user settings

## 11. Security Considerations

1. All routes require authentication (`@login_required`)
2. Password changes require current password verification
3. Email uniqueness is enforced
4. Form validation prevents malicious input
5. CSRF protection through Flask-WTF

## 12. Customization

You can customize the implementation by:

1. Adding more languages to the `SettingsForm`
2. Adding more currency formats
3. Modifying the date format options
4. Adding additional notification preferences
5. Styling the templates to match your brand

## 13. Error Handling

The implementation includes:

1. Database error handling with rollbacks
2. Form validation errors display
3. User-friendly error messages
4. Logging of errors for debugging

## 14. Performance Considerations

1. Database queries are optimized
2. Form validation happens on both client and server
3. JavaScript enhances UX without breaking functionality
4. Minimal additional database load

This completes the integration of user profile and settings management into your BigCapital application!