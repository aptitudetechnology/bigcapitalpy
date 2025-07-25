# Instructions for Creating Jinja2 Templates for the Organization Section

**Goal:**  
Create Jinja2 templates for an "Organization" section in the Flask app, inspired by the React version's organization settings and metadata features.  
**Do not create any new CSS. Use only Bootstrap classes and existing styles.**

## 1. Template Structure

- Create a new template at `templates/organization/index.html`.
- The page should display the organization's key information:
  - Organization Name
  - Tax Number
  - Industry
  - Address
  - Language
  - (Optionally) any other metadata fields you find relevant
- Add an "Edit" button that links to an organization edit form (e.g., `/organization/edit`).

## 2. Example Jinja2 Template (`organization/index.html`)

```jinja
{% extends "base.html" %}
{% block title %}Organization Details{% endblock %}

{% block content %}
<div class="container">
    <h1 class="mb-4">Organization</h1>
    <div class="card">
        <div class="card-body">
            <dl class="row">
                <dt class="col-sm-3">Name</dt>
                <dd class="col-sm-9">{{ organization.name }}</dd>

                <dt class="col-sm-3">Tax Number</dt>
                <dd class="col-sm-9">{{ organization.tax_number }}</dd>

                <dt class="col-sm-3">Industry</dt>
                <dd class="col-sm-9">{{ organization.industry }}</dd>

                <dt class="col-sm-3">Address</dt>
                <dd class="col-sm-9">{{ organization.address }}</dd>

                <dt class="col-sm-3">Language</dt>
                <dd class="col-sm-9">{{ organization.language }}</dd>
            </dl>
            <a href="{{ url_for('organization.edit') }}" class="btn btn-primary">Edit Organization</a>
        </div>
    </div>
</div>
{% endblock %}
```

## 3. Edit Form Template (`organization/edit.html`)

- Use Flask-WTF for the form.
- Render fields for all organization attributes.
- Use Bootstrap form classes.

## 4. Controller/Route

- The Flask route should provide an `organization` object to the template, similar to how the React version uses organization context.
- The edit form should POST updates and redirect back to the details page on success.

## 5. No New CSS

- Do not add or modify any CSS files.
- Use only Bootstrap and existing styles.

---

**Summary:**  
- Scaffold `organization/index.html` and `organization/edit.html` as described.  
- Use Bootstrap for layout and styling.  
- Do not create or modify any CSS.  
- Follow Flask/Jinja2 and project conventions for template inheritance and form handling.
