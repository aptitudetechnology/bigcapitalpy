# Help/Support System

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
