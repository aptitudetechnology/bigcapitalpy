# Users & Permissions
#
# Note: This section is for admin-level user, role, and permission management (RBAC). For user self-service profile and settings, see `user-management.md`.

## Claude Implementation Instructions

**Goal:** Implement a full Users & Permissions management system for the accounting app, including UI, backend, and routing.
**Instructions for Claude:**
Start by generating the UI Jinja2 templates for user and permission management, then work backwards to implement the backend code, forms, and blueprints. Follow the order of sections below.

**Scope:**
- Admins can create, edit, and delete users.
- Admins can assign roles and permissions to users.
- Admins can manage roles and permission sets.
- All sensitive actions must be protected by permission checks.

**Related:**
- For user self-service (profile, password, preferences), see `user-management.md`.

### 1. Jinja2 Templates
- Create `users/index.html`, `users/new.html`, `users/edit.html`, `users/show.html` for user management (list, create, edit, view).
- Create `permissions/index.html` for managing roles and permissions.
- Add forms for user creation/editing and role assignment using Flask-WTF.
- Add navigation links in the main menu for Users & Permissions.

### 2. Python Backend (Flask)
- Create a `users` blueprint and a `permissions` blueprint in `packages/server/src/modules/`.
- Implement RESTful routes: `index`, `new`, `show`, `edit`, `delete` for users and permissions.
- Use SQLAlchemy models for User, Role, and Permission, with many-to-many relationships.
- Add organization filtering and timestamps.
- Add error handling and login protection.

### 3. Forms
- Use Flask-WTF forms for user and permission management.
- Add validators for email, password, and unique constraints.

### 4. JavaScript
- Add JS for user/role assignment, modals, and AJAX (for delete or inline actions).

### 5. Libraries to Use
- **Flask-Login**: For authentication and user session management.
- **Flask-Principal** or **Flask-Security**: For role and permission management.
- **Flask-WTF**: For forms.
- **Bootstrap**: For UI.
- **Pandas**: For exporting user lists if needed.

### 6. Testing
- Add pytest or unittest tests for all user and permission routes and forms.

### 7. Documentation
- Document all endpoints, templates, and permission logic.

---
**Tip:** Use role-based access control (RBAC) patterns. Allow admins to assign roles and permissions to users. Ensure all sensitive actions are protected by appropriate permission checks.

**Important:** Do not generate any CSS. Use Bootstrap classes only for styling.
