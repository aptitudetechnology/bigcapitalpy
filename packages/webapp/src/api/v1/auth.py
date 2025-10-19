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

@auth_api_bp.route('/api-key', methods=['POST'])
def generate_api_key():
    """Generate a new API key for the current user"""
    if not current_user.is_authenticated:
        return api_error('Not authenticated', 401)
    
    try:
        api_key = current_user.generate_api_key()
        db.session.commit()
        
        return api_response(
            data={
                'api_key': api_key,
                'created_at': current_user.api_key_created_at.isoformat()
            },
            message='API key generated successfully'
        )
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to generate API key: {str(e)}', 500)

@auth_api_bp.route('/api-key', methods=['DELETE'])
def revoke_api_key():
    """Revoke the current API key"""
    if not current_user.is_authenticated:
        return api_error('Not authenticated', 401)
    
    try:
        current_user.revoke_api_key()
        db.session.commit()
        
        return api_response(message='API key revoked successfully')
    except Exception as e:
        db.session.rollback()
        return api_error(f'Failed to revoke API key: {str(e)}', 500)

@auth_api_bp.route('/api-key', methods=['GET'])
def get_api_key_info():
    """Get information about the current API key"""
    if not current_user.is_authenticated:
        return api_error('Not authenticated', 401)
    
    if current_user.api_key:
        return api_response(data={
            'has_api_key': True,
            'created_at': current_user.api_key_created_at.isoformat() if current_user.api_key_created_at else None,
            'last_used': None  # Could be added later with usage tracking
        })
    else:
        return api_response(data={
            'has_api_key': False
        })
