# User Management (Profile, Settings)

## Description
Pages and features for user profile management and application/user settings.

## Status
Not yet implemented.

## Claude Implementation Instructions

**Goal:** Implement user profile and settings management.

### 1. Jinja2 Templates
- Create `profile.html` and `settings.html` for user info and preferences.
- Add forms for updating user data and settings.
- Add links in the navbar/user menu.

### 2. Python Backend (Flask)
- Create a `user` blueprint with routes for profile view/edit and settings.
- Use Flask-Login for user authentication.
- Use SQLAlchemy models for user data and settings.

### 3. Forms
- Use Flask-WTF for profile/settings forms.
- Add validators for email, password, etc.

### 4. JavaScript
- Add JS for toggling settings, password visibility, etc.

### 5. Libraries to Use
- **Flask-Login**: For authentication.
- **Flask-WTF**: For forms.
- **Bootstrap**: For UI.

### 6. Testing
- Add tests for profile and settings routes and forms.

---
**Tip:** Allow users to update their password and notification preferences.
