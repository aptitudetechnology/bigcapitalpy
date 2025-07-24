# Notification System

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
