# Estimates & Credit Notes
## Description
Core accounting features for managing estimates (quotes) and credit notes.

## Status
Not yet implemented.

## Claude Implementation Instructions

**Goal:** Implement full CRUD for Estimates and Credit Notes, including UI, backend, and routing.
**Instructions for Claude:**
Start by generating the UI Jinja2 templates for estimates and credit notes, then work backwards to implement the backend code, forms, and blueprints. Follow the order of sections below.

**Scope:**
- Users can create, view, edit, and delete estimates and credit notes.
- Admins can approve or reject credit notes (optional).
- All actions are organization-scoped.

### 1. Jinja2 Templates
- Create `estimates/index.html`, `estimates/new.html`, `estimates/edit.html`, `estimates/show.html` (and same for credit notes) using Bootstrap for styling.
- Add forms for creation/editing using Flask-WTF.
- Add navigation dropdowns and links in the main menu.

### 2. Python Backend (Flask)
- Create a `Blueprint` for `estimates` and `credit_notes` in `packages/server/src/modules/`.
- Implement RESTful routes: `index`, `new`, `show`, `edit`, `delete` for each entity.
- Use SQLAlchemy models for both entities, with organization filtering and timestamps.
- Add error handling and login protection.

### 3. Forms
- Use Flask-WTF forms for validation.
- Add custom validators (e.g., unique code).

### 4. JavaScript
- Add JS for dropdowns, modals, and AJAX (if needed for delete or inline actions).

### 5. Libraries to Use
- **Pandas**: For advanced data manipulation or export.
- **Flask-WTF**: For forms.
- **Bootstrap**: For UI.
- **Flask-Login**: For authentication.

### 6. Testing
- Add pytest or unittest tests for all routes and forms.

---
**Tip:** Use code generation and DRY patterns to avoid duplication between estimates and credit notes.

**Important:** Do not generate any CSS. Use Bootstrap classes only for styling.

## Description
Core accounting features for managing estimates (quotes) and credit notes.

## Status
Not yet implemented.

## Claude Implementation Instructions

**Goal:** Implement full CRUD for Estimates and Credit Notes, including UI, backend, and routing.

### 1. Jinja2 Templates
- Create `estimates/index.html`, `estimates/new.html`, `estimates/edit.html`, `estimates/show.html` (and same for credit notes) using Bootstrap for styling.
- Add forms for creation/editing using Flask-WTF.
- Add navigation dropdowns and links in the main menu.

### 2. Python Backend (Flask)
- Create a `Blueprint` for `estimates` and `credit_notes` in `packages/server/src/modules/`.
- Implement RESTful routes: `index`, `new`, `show`, `edit`, `delete` for each entity.
- Use SQLAlchemy models for both entities, with organization filtering and timestamps.
- Add error handling and login protection.

### 3. Forms
- Use Flask-WTF forms for validation.
- Add custom validators (e.g., unique code).

### 4. JavaScript
- Add JS for dropdowns, modals, and AJAX (if needed for delete or inline actions).

### 5. Libraries to Use
- **Pandas**: For advanced data manipulation or export.
- **Flask-WTF**: For forms.
- **Bootstrap**: For UI.
- **Flask-Login**: For authentication.

### 6. Testing
- Add pytest or unittest tests for all routes and forms.

### 7. Documentation
- Document all endpoints and templates.

---
**Tip:** Use code generation and DRY patterns to avoid duplication between estimates and credit notes.
