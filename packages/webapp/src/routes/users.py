@users_bp.route('/settings/edit', methods=['GET', 'POST'])
@login_required
def edit_settings():
    form = SettingsForm()
    if form.validate_on_submit():
        # Save settings logic here
        flash('Settings updated.', 'success')
        return redirect(url_for('users.settings'))
    return render_template('system/users/edit_settings.html', form=form)
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from packages.server.src.models import User
from packages.server.src.database import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

users_bp = Blueprint('users', __name__, url_prefix='/system/user')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=255)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    submit = SubmitField('Update Profile')

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    print("Type of user:", type(user))
    print("User attributes:", dir(user))
    # Unwrap LocalProxy if needed
    user_real = user._get_current_object() if hasattr(user, '_get_current_object') else user
    print("Type of user_real:", type(user_real))
    print("User_real attributes:", dir(user_real))
    if not hasattr(user_real, 'language'):
        print("User object missing 'language' attribute")
    else:
        print("User language:", user_real.language)
    form = ProfileForm(obj=user_real)
    if form.validate_on_submit():
        form.populate_obj(user_real)
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile.', 'error')
        return redirect(url_for('users.profile'))
    return render_template('system/users/profile.html', form=form, user=user_real)

class SettingsForm(FlaskForm):
    # Add settings fields as needed
    submit = SubmitField('Save Settings')
    
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

@users_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        # Add password validation logic here
        if not user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
        elif form.new_password.data != form.confirm_password.data:
            flash('New passwords do not match.', 'error')
        else:
            user.set_password(form.new_password.data)
            try:
                db.session.commit()
                flash('Password changed successfully.', 'success')
                return redirect(url_for('users.change_password'))
            except Exception as e:
                db.session.rollback()
                flash('Error changing password.', 'error')
    return render_template('system/users/change_password.html', form=form)

@users_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        # Save settings logic here
        flash('Settings saved.', 'success')
        return redirect(url_for('users.settings'))
    return render_template('system/users/settings.html', form=form)
