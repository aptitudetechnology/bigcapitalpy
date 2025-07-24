# User Management (Profile, Settings)
#
# Note: This section is for user self-service profile and settings management. For admin-level user/role/permission management, see `Users-Permissions.md`.

## Description
Pages and features for user profile management and application/user settings.

## Status
Not yet implemented.

## Claude Implementation Instructions

**Goal:** Implement user profile and settings management.

**Instructions for Claude:**
Start by generating the UI Jinja2 templates for profile and settings pages, then work backwards to implement the backend code, forms, and blueprints. Follow the order of sections below.

**Scope:**
- Users can view and update their own profile information.
- Users can change their password and notification preferences.
- Users can update personal settings (e.g., language, timezone).
- No admin or role management here (see `Users-Permissions.md`).

**Related:**
- For admin user/role/permission management, see `Users-Permissions.md`.

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

**Important:** Do not generate any CSS. Use Bootstrap classes only for styling.
