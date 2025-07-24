# Notification System
## Description
System for user notifications (e.g., new invoice, payment overdue, report generated).

## Status
Not yet implemented.

## Claude Implementation Instructions

**Goal:** Implement a real-time notification system for user events.
**Instructions for Claude:**
Start by generating the UI Jinja2 templates for notification panels/pages, then work backwards to implement the backend code, forms, and blueprints. Follow the order of sections below.

**Scope:**
- Users receive notifications for key events (invoice, payment, etc).
- Users can view, mark as read, and clear notifications.
- Admins can broadcast notifications (optional).

### 1. Jinja2 Templates
- Add a notification dropdown/panel in the navbar.
- Create a notifications page to list all user notifications.

### 2. Python Backend (Flask)
- Create a `notifications` blueprint with routes for listing, marking as read, and clearing notifications.
- Use a SQLAlchemy model for notifications (user_id, message, read, created_at).
- Add logic to generate notifications on key events (invoice created, payment overdue, etc).

### 3. JavaScript
- Use JS (and optionally WebSockets with Flask-SocketIO) for real-time updates.
- Add AJAX for marking notifications as read.

### 4. Libraries to Use
- **Flask-SocketIO**: For real-time notifications.
- **Bootstrap**: For UI.

### 5. Testing
- Add tests for notification creation, listing, and marking as read.

---
**Tip:** Start with polling/AJAX if real-time is too complex initially.

**Important:** Do not generate any CSS. Use Bootstrap classes only for styling.

## Description
System for user notifications (e.g., new invoice, payment overdue, report generated).

## Status
Not yet implemented.

## Claude Implementation Instructions

**Goal:** Implement a real-time notification system for user events.

### 1. Jinja2 Templates
- Add a notification dropdown/panel in the navbar.
- Create a notifications page to list all user notifications.

### 2. Python Backend (Flask)
- Create a `notifications` blueprint with routes for listing, marking as read, and clearing notifications.
- Use a SQLAlchemy model for notifications (user_id, message, read, created_at).
- Add logic to generate notifications on key events (invoice created, payment overdue, etc).

### 3. JavaScript
- Use JS (and optionally WebSockets with Flask-SocketIO) for real-time updates.
- Add AJAX for marking notifications as read.

### 4. Libraries to Use
- **Flask-SocketIO**: For real-time notifications.
- **Bootstrap**: For UI.

### 5. Testing
- Add tests for notification creation, listing, and marking as read.

---
**Tip:** Start with polling/AJAX if real-time is too complex initially.
