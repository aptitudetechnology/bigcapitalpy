"""
Authentication API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from packages.server.src.models import User
from packages.server.src.database import db
from ..utils import api_response, api_error, validate_json_request, serialize_model

auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/login', methods=['POST'])
@validate_json_request(['email', 'password'])
def login():
    """Authenticate user and create session"""
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    if not email or not password:
        return api_error('Email and password are required', 400)
    
    user = User.query.filter_by(email=email, is_active=True).first()
    
    if not user or not user.check_password(password):
        return api_error('Invalid email or password', 401)
    
    login_user(user, remember=data.get('remember', False))
    
    user_data = serialize_model(user, exclude=['password_hash'])
    user_data['organization'] = serialize_model(user.organization)
    
    return api_response(
        data={'user': user_data},
        message='Login successful'
    )

@auth_api_bp.route('/logout', methods=['POST'])
def logout():
    """Logout current user"""
    logout_user()
    return api_response(message='Logout successful')

@auth_api_bp.route('/me', methods=['GET'])
def me():
    """Get current user information"""
    if not current_user.is_authenticated:
        return api_error('Not authenticated', 401)
    
    user_data = serialize_model(current_user, exclude=['password_hash'])
    user_data['organization'] = serialize_model(current_user.organization)
    
    return api_response(data={'user': user_data})

@auth_api_bp.route('/check', methods=['GET'])
def check():
    """Check authentication status"""
    return api_response(data={
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None
    })
