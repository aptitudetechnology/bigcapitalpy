"""
Authentication API endpoints for React frontend
These endpoints provide JWT-based authentication for the React app
"""

import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from packages.server.src.models import User, Organization
from packages.server.src.database import db

auth_api_bp = Blueprint('auth_api', __name__)

def generate_token(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'organization_id': user.organization_id,
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

@auth_api_bp.route('/signin', methods=['POST'])
def signin():
    """JWT-based login for React app"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'errors': {'message': 'No data provided'}}), 400

        email = data.get('email', '').lower().strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'errors': {'message': 'Email and password are required'}}), 400

        user = User.query.filter_by(email=email, is_active=True).first()

        if not user or not user.check_password(password):
            return jsonify({'errors': {'message': 'Invalid email or password'}}), 401

        # Generate JWT token
        token = generate_token(user)

        # Get organization info
        organization = user.organization

        response_data = {
            'access_token': token,
            'user_id': user.id,
            'organization_id': user.organization_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'tenant': {
                'id': organization.id,
                'name': organization.name,
                'currency': organization.currency,
                'timezone': organization.timezone
            } if organization else None
        }

        return jsonify({'data': response_data}), 200

    except Exception as e:
        current_app.logger.error(f"Signin error: {str(e)}")
        return jsonify({'errors': {'message': 'Internal server error'}}), 500

@auth_api_bp.route('/signup', methods=['POST'])
def signup():
    """User registration for React app"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'errors': {'message': 'No data provided'}}), 400

        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not all([email, password, first_name, last_name]):
            return jsonify({'errors': {'message': 'All fields are required'}}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'errors': {'message': 'User already exists'}}), 409

        # For MVP, we'll create a default organization if none exists
        # In production, this would be more sophisticated
        organization = Organization.query.first()
        if not organization:
            organization = Organization(
                name="Default Organization",
                legal_name="Default Organization Inc",
                currency="USD",
                timezone="UTC"
            )
            db.session.add(organization)
            db.session.commit()

        # Create user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization_id=organization.id,
            role='user'
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Generate token for immediate login
        token = generate_token(user)

        response_data = {
            'access_token': token,
            'user_id': user.id,
            'organization_id': user.organization_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        }

        return jsonify({'data': response_data}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Signup error: {str(e)}")
        return jsonify({'errors': {'message': 'Internal server error'}}), 500

@auth_api_bp.route('/meta', methods=['GET'])
def meta():
    """Get authentication metadata"""
    try:
        # This would typically return app configuration, features, etc.
        # For MVP, return basic metadata
        metadata = {
            'version': '1.0.0',
            'features': {
                'multi_tenant': True,
                'api_enabled': True,
                'demo_mode': True
            },
            'supported_currencies': ['USD', 'EUR', 'GBP', 'AUD'],
            'default_currency': 'USD'
        }

        return jsonify({'data': metadata}), 200

    except Exception as e:
        current_app.logger.error(f"Meta error: {str(e)}")
        return jsonify({'errors': {'message': 'Internal server error'}}), 500

@auth_api_bp.route('/send_reset_password', methods=['POST'])
def send_reset_password():
    """Send password reset email"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()

        if not email:
            return jsonify({'errors': {'message': 'Email is required'}}), 400

        # For MVP, just return success (email functionality not implemented)
        # In production, this would send an actual reset email
        return jsonify({'data': {'message': 'Password reset email sent'}}), 200

    except Exception as e:
        current_app.logger.error(f"Send reset password error: {str(e)}")
        return jsonify({'errors': {'message': 'Internal server error'}}), 500

@auth_api_bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    """Reset password with token"""
    try:
        data = request.get_json()
        new_password = data.get('password', '')

        if not new_password:
            return jsonify({'errors': {'message': 'New password is required'}}), 400

        # For MVP, just return success (token validation not implemented)
        # In production, this would validate the token and update the password
        return jsonify({'data': {'message': 'Password reset successfully'}}), 200

    except Exception as e:
        current_app.logger.error(f"Reset password error: {str(e)}")
        return jsonify({'errors': {'message': 'Internal server error'}}), 500