---
### 🐛 Bug Report: `BuildError` on `url_for('user.edit_profile')` in `profile.html`

#### Description
A `BuildError` is raised when rendering `profile.html` due to an incorrect endpoint reference:

```html
<a href="{{ url_for('user.edit_profile') }}" class="btn btn-primary me-2">
```

The error message suggests:

```
werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'user.edit_profile'. Did you mean 'users.profile' instead?
```

#### Root Cause
The template references an endpoint `user.edit_profile`, but Flask cannot find it. This is due to a mismatch between the endpoint name used in `url_for()` and the actual blueprint name.

The `users` blueprint is likely defined as:

```python
users_bp = Blueprint('users', __name__, url_prefix='/users')
```

This makes all routes under this blueprint use the `users.*` namespace — **not** `user.*`.

#### Fix
Update all instances in `profile.html` like so:

**Before:**
```jinja2
url_for('user.edit_profile')
url_for('user.change_password')
url_for('user.settings')
```

**After:**
```jinja2
url_for('users.edit_profile')
url_for('users.change_password')
url_for('users.settings')
```

#### Suggested Improvements
* [ ] Audit all templates for hardcoded endpoint prefixes (`user.*`) and standardize according to blueprint names.
* [ ] Optionally add custom endpoint names when defining routes for clarity:

```python
@users_bp.route('/profile/edit', endpoint='edit_profile')
```

#### Environment
* **Flask version**: 3.x
* **Python version**: 3.12
* **Project structure**: Blueprint-based (`users_bp`)
---
