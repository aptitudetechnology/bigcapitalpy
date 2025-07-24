# Help/Support System
## Description
Pages and features for user help, documentation, and support.

## Status
Not yet implemented.

## Claude Implementation Instructions

**Goal:** Implement a help/support system with documentation and contact options.
**Instructions for Claude:**
Start by generating the UI Jinja2 templates for help/support pages, then work backwards to implement the backend code, forms, and blueprints. Follow the order of sections below.

**Scope:**
- Users can access help pages, FAQs, and guides.
- Users can submit support requests or contact support.
- Admins can manage help content (optional).

### 1. Jinja2 Templates
- Create `help/index.html` with FAQ, guides, and contact form.
- Add help links to the main navigation and relevant pages.

### 2. Python Backend (Flask)
- Create a `help` blueprint with routes for index, FAQ, and contact.
- Implement a contact form using Flask-WTF (send email or store message).

### 3. Forms
- Use Flask-WTF for contact/support forms.
- Add validators for email, message, etc.

### 4. JavaScript
- Add JS for toggling FAQ sections or submitting contact forms via AJAX.

### 5. Libraries to Use
- **Flask-Mail**: For sending support emails.
- **Flask-WTF**: For forms.
- **Bootstrap**: For UI.

### 6. Testing
- Add tests for help pages and contact form submission.

---
**Tip:** Link to external documentation or knowledge base if available.

**Important:** Do not generate any CSS. Use Bootstrap classes only for styling.

## Description
Pages and features for user help, documentation, and support.

## Status
Not yet implemented.

## Claude Implementation Instructions

**Goal:** Implement a help/support system with documentation and contact options.

### 1. Jinja2 Templates
- Create `help/index.html` with FAQ, guides, and contact form.
- Add help links to the main navigation and relevant pages.

### 2. Python Backend (Flask)
- Create a `help` blueprint with routes for index, FAQ, and contact.
- Implement a contact form using Flask-WTF (send email or store message).

### 3. JavaScript
- Add JS for toggling FAQ sections or submitting contact forms via AJAX.

### 4. Libraries to Use
- **Flask-Mail**: For sending support emails.
- **Flask-WTF**: For forms.
- **Bootstrap**: For UI.

### 5. Testing
- Add tests for help pages and contact form submission.

---
**Tip:** Link to external documentation or knowledge base if available.
