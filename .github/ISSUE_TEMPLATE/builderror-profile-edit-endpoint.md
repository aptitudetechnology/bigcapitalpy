---
## 🐛 Bug: `BuildError` for `url_for('users.edit_profile')` — Missing Endpoint

### Summary
A `BuildError` is raised when rendering the `profile.html` template due to a missing endpoint:

```jinja2
<a href="{{ url_for('users.edit_profile') }}">
```

The error traceback suggests:

```
BuildError: Could not build url for endpoint 'users.edit_profile'. Did you mean 'users.profile' instead?
```

### Root Cause
The route `users.edit_profile` does **not** exist. Flask only knows about `users.profile`, which implies:

* The function handling `/users/profile/edit` does **not** match the `edit_profile` endpoint name.
* `url_for()` is referencing a route that is **not registered** with Flask.

### Diagnosis Steps
1. **Check the route definition in `routes/users.py`**:

   ```python
   @users_bp.route('/profile/edit', methods=['GET', 'POST'])
   def profile_edit():
       ...
   ```

   If the function is named `profile_edit`, the endpoint name becomes `users.profile_edit` (not `edit_profile`).

2. **Check blueprint name:**

   ```python
   users_bp = Blueprint('users', __name__, url_prefix='/users')
   ```

   This confirms the namespace prefix for all endpoints is `users.*`.

3. **List all endpoints (optional debug snippet):**

   ```python
   from flask import current_app
   for rule in current_app.url_map.iter_rules():
       print(f"{rule.endpoint:30} -> {rule.rule}")
   ```

### ✅ Recommended Fix
Update the Jinja template to match the actual route function name:

```jinja2
<a href="{{ url_for('users.profile_edit') }}">
```

OR define an explicit endpoint name in the route:

```python
@users_bp.route('/profile/edit', methods=['GET', 'POST'], endpoint='edit_profile')
def profile_edit():
    ...
```

Then keep the Jinja usage:

```jinja2
<a href="{{ url_for('users.edit_profile') }}">
```

### Suggested Improvements
* [ ] Audit all `url_for('users.*')` calls in templates and ensure endpoint names match.
* [ ] Standardize endpoint naming using the `endpoint=` parameter in route decorators.
* [ ] Add a utility CLI or shell script to print registered routes for dev inspection.

---
