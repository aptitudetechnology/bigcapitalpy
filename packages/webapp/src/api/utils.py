"""
API Utilities and Helper Functions
"""

from functools import wraps
from flask import jsonify, request, current_app
from flask_login import current_user
import jwt
from datetime import datetime, timedelta
from packages.server.src.models import User

def api_response(data=None, message=None, status_code=200, errors=None):
    """Standardized API response format"""
    response = {
        'success': status_code < 400,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code

def api_error(message, status_code=400, errors=None):
    """Standardized API error response"""
    return api_response(message=message, status_code=status_code, errors=errors)

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, we'll use session-based auth (login_required equivalent)
        # In the future, this can be extended to support API keys or JWT tokens
        if not current_user.is_authenticated:
            return api_error('Authentication required', 401)
        return f(*args, **kwargs)
    return decorated_function

def validate_json_request(required_fields=None):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return api_error('Content-Type must be application/json', 400)
            
            data = request.get_json()
            if not data:
                return api_error('Request body must contain valid JSON', 400)
            
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    return api_error(
                        f'Missing required fields: {", ".join(missing_fields)}',
                        400,
                        {'missing_fields': missing_fields}
                    )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def paginate_query(query, page=1, per_page=20, max_per_page=100):
    """Paginate a SQLAlchemy query"""
    if per_page > max_per_page:
        per_page = max_per_page
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page * per_page < total
        }
    }

def get_pagination_params():
    """Extract pagination parameters from request"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Ensure positive values
    page = max(1, page)
    per_page = max(1, min(100, per_page))  # Cap at 100 items per page
    
    return page, per_page

def serialize_model(model, fields=None, exclude=None):
    """Serialize SQLAlchemy model to dictionary"""
    if model is None:
        return None
    
    result = {}
    
    # Get all columns if no specific fields requested
    if fields is None:
        fields = [column.name for column in model.__table__.columns]
    
    for field in fields:
        if exclude and field in exclude:
            continue
            
        value = getattr(model, field, None)
        
        # Handle special types
        if hasattr(value, 'isoformat'):  # datetime/date objects
            value = value.isoformat()
        elif hasattr(value, '__float__'):  # Decimal objects
            value = float(value)
        elif hasattr(value, 'value'):  # Enum objects
            value = value.value
        
        result[field] = value
    
    return result
