from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pytz

from . import user_bp
from ..models import User, db
from .forms import ProfileForm, PasswordForm, SettingsForm


@user_bp.route('/profile')
@login_required
def profile():
    """Display user profile."""
    return render_template('system/users/profile.html', user=current_user)


@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile information."""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if email is being changed and if it's already taken
        if form.email.data != current_user.email:
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email address is already in use.', 'error')
                return render_template('system/users/edit_profile.html', form=form)
        
        # Update user information
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'error')
            current_app.logger.error(f'Profile update error: {str(e)}')
    
    return render_template('system/users/edit_profile.html', form=form)


@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    form = PasswordForm()
    
    if form.validate_on_submit():
        # Verify current password
        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('user/change_password.html', form=form)
        
        # Update password
        current_user.password_hash = generate_password_hash(form.new_password.data)
        current_user.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('user.profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while changing your password.', 'error')
            current_app.logger.error(f'Password change error: {str(e)}')
    
    return render_template('system/users/change_password.html', form=form)


@user_bp.route('/settings')
@login_required
def settings():
    """Display user settings."""
    return render_template('system/users/settings.html', user=current_user)


@user_bp.route('/settings/edit', methods=['GET', 'POST'])
@login_required
def edit_settings():
    """Edit user settings."""
    form = SettingsForm(obj=current_user)
    
    if form.validate_on_submit():
        # Update user settings
        current_user.language = form.language.data
        current_user.timezone = form.timezone.data
        current_user.date_format = form.date_format.data
        current_user.currency_format = form.currency_format.data
        current_user.email_notifications = form.email_notifications.data
        current_user.dashboard_notifications = form.dashboard_notifications.data
        current_user.marketing_emails = form.marketing_emails.data
        current_user.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('user.settings'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your settings.', 'error')
            current_app.logger.error(f'Settings update error: {str(e)}')
    
    return render_template('system/users/edit_settings.html', form=form)


def get_timezone_choices():
    """Get list of timezone choices for forms."""
    timezones = []
    for tz in pytz.all_timezones:
        timezones.append((tz, tz))
    return sorted(timezones)