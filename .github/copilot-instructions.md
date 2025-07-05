# GitHub Copilot Instructions for Flask Development

## Project Context
This is a Flask-based accounting application (BigCapitalPy) with the following structure:
- **Backend**: Flask with SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend**: Jinja2 templates with Bootstrap styling
- **Database**: SQLAlchemy models with PostgreSQL
- **Authentication**: Flask-Login for user sessions
- **Forms**: Flask-WTF with WTForms validation

## Key Architecture Patterns

### 1. Blueprint Organization
```python
# Each feature should be organized as a blueprint
from flask import Blueprint
feature_bp = Blueprint('feature_name', __name__)

# Routes follow RESTful patterns:
@feature_bp.route('/')              # GET - index/list
@feature_bp.route('/new')           # GET/POST - create form
@feature_bp.route('/<int:id>')      # GET - show detail
@feature_bp.route('/<int:id>/edit') # GET/POST - edit form  
@feature_bp.route('/<int:id>/delete') # POST - delete
```

### 2. Form Handling Pattern
```python
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

class EntityForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    # ... other fields

@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = EntityForm()
    if form.validate_on_submit():
        # Create entity
        # Save to database
        flash('Success message', 'success')
        return redirect(url_for('blueprint.index'))
    return render_template('template.html', form=form)
```

### 3. Database Model Pattern
```python
from packages.server.src.models import db

class Entity(db.Model):
    __tablename__ = 'entities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    organization_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Coding Standards

### 1. Route Naming Conventions
- Use descriptive function names that match the action
- Common patterns: `index`, `new`, `show`, `edit`, `delete`
- API routes: prefix with `api_` (e.g., `api_hierarchy`)

### 2. Template URL Generation
```python
# In templates, always use url_for with blueprint.function_name
{{ url_for('accounts.new') }}      # NOT 'accounts.create'
{{ url_for('accounts.show', account_id=account.id) }}
{{ url_for('accounts.edit', account_id=account.id) }}
```

### 3. Error Handling
```python
try:
    db.session.add(entity)
    db.session.commit()
    flash('Success message', 'success')
except Exception as e:
    db.session.rollback()
    flash('Error message', 'error')
```

### 4. Security Patterns
```python
# Always use login_required decorator
@bp.route('/')
@login_required
def index():
    pass

# Filter by organization for multi-tenant
query = Entity.query.filter(Entity.organization_id == current_user.organization_id)
```

## Common Patterns to Implement

### 1. CRUD Operations
When creating CRUD for a new entity:
```python
# Index - List all
@bp.route('/')
@login_required
def index():
    entities = Entity.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('entities/index.html', entities=entities)

# New - Create form
@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = EntityForm()
    if form.validate_on_submit():
        entity = Entity(
            name=form.name.data,
            organization_id=current_user.organization_id
        )
        db.session.add(entity)
        db.session.commit()
        return redirect(url_for('entities.index'))
    return render_template('entities/new.html', form=form)

# Show - Display single entity
@bp.route('/<int:entity_id>')
@login_required
def show(entity_id):
    entity = Entity.query.get_or_404(entity_id)
    return render_template('entities/show.html', entity=entity)

# Edit - Update form
@bp.route('/<int:entity_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(entity_id):
    entity = Entity.query.get_or_404(entity_id)
    form = EntityForm(obj=entity)
    if form.validate_on_submit():
        form.populate_obj(entity)
        db.session.commit()
        return redirect(url_for('entities.show', entity_id=entity.id))
    return render_template('entities/edit.html', form=form, entity=entity)

# Delete - Remove entity
@bp.route('/<int:entity_id>/delete', methods=['POST'])
@login_required
def delete(entity_id):
    entity = Entity.query.get_or_404(entity_id)
    db.session.delete(entity)
    db.session.commit()
    return redirect(url_for('entities.index'))
```

### 2. Form Validation
```python
# Custom validators
def unique_code_validator(form, field):
    existing = Entity.query.filter_by(code=field.data).first()
    if existing:
        raise ValidationError('Code already exists')

# Form with validation
class EntityForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired(), unique_code_validator])
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=255)])
```

### 3. Template Structure
```html
<!-- templates/entities/index.html -->
{% extends "base.html" %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>Entities</h1>
    <a href="{{ url_for('entities.new') }}" class="btn btn-primary">New Entity</a>
</div>

<div class="table-responsive">
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Code</th>
                <th>Name</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for entity in entities %}
            <tr>
                <td>{{ entity.code }}</td>
                <td>{{ entity.name }}</td>
                <td>
                    <a href="{{ url_for('entities.show', entity_id=entity.id) }}" class="btn btn-sm btn-outline-primary">View</a>
                    <a href="{{ url_for('entities.edit', entity_id=entity.id) }}" class="btn btn-sm btn-outline-secondary">Edit</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

## Common Mistakes to Avoid

1. **Wrong endpoint names**: Use function names, not route paths
   - ❌ `url_for('accounts.create')` 
   - ✅ `url_for('accounts.new')`

2. **Missing organization filtering**: Always filter by organization
   - ✅ `Entity.query.filter_by(organization_id=current_user.organization_id)`

3. **Forgetting error handling**: Always wrap database operations in try/catch

4. **Missing login_required**: All routes should require authentication

5. **Hardcoded values**: Use current_user.organization_id instead of hardcoded IDs

## Database Patterns

### 1. Model Relationships
```python
class Account(db.Model):
    # Self-referencing for parent/child accounts
    parent_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    children = db.relationship('Account', backref=db.backref('parent', remote_side=[id]))
    
    # Organization relationship
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization', backref='accounts')
```

### 2. Query Patterns
```python
# With filtering and ordering
accounts = Account.query.filter_by(
    organization_id=current_user.organization_id,
    is_active=True
).order_by(Account.code, Account.name).all()

# With search
if search:
    query = query.filter(
        db.or_(
            Account.name.ilike(f'%{search}%'),
            Account.code.ilike(f'%{search}%')
        )
    )
```

## API Endpoints
```python
@bp.route('/api/entities')
@login_required
def api_entities():
    entities = Entity.query.filter_by(organization_id=current_user.organization_id).all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'code': e.code
    } for e in entities])
```

## Testing Patterns
```python
def test_create_entity():
    with app.test_client() as client:
        # Login first
        # Post to create endpoint
        response = client.post('/entities/new', data={
            'name': 'Test Entity',
            'code': 'TEST'
        })
        assert response.status_code == 302  # Redirect after success
```

Remember: Always follow the existing patterns in the codebase and maintain consistency with the established architecture.