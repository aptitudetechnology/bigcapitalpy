# packages/webapp/src/routes/organization.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length, Email, URL
from packages.server.src.models import Organization, db

organization_bp = Blueprint('organization', __name__, url_prefix='/organization')


class OrganizationForm(FlaskForm):
    """Form for editing organization information."""
    name = StringField('Organization Name', 
                      validators=[DataRequired(), Length(min=2, max=200)],
                      render_kw={'placeholder': 'Enter organization name'})
    
    tax_number = StringField('Tax Number/ABN', 
                            validators=[Optional(), Length(max=50)],
                            render_kw={'placeholder': 'e.g., 12 345 678 901'})
    
    industry = StringField('Industry', 
                          validators=[Optional(), Length(max=100)],
                          render_kw={'placeholder': 'e.g., Professional Services'})
    
    address = TextAreaField('Address', 
                           validators=[Optional(), Length(max=500)],
                           render_kw={'placeholder': 'Complete business address'})
    
    language = SelectField('Language', 
                          choices=[
                              ('en', 'English'),
                              ('es', 'Spanish'),
                              ('fr', 'French'),
                              ('de', 'German'),
                              ('it', 'Italian'),
                              ('pt', 'Portuguese'),
                              ('zh', 'Chinese'),
                              ('ja', 'Japanese'),
                              ('ko', 'Korean'),
                              ('ar', 'Arabic'),
                          ],
                          default='en',
                          validators=[DataRequired()])
    
    phone = StringField('Phone', 
                       validators=[Optional(), Length(max=20)],
                       render_kw={'placeholder': '+1 (555) 123-4567'})
    
    email = StringField('Email', 
                       validators=[Optional(), Email(), Length(max=120)],
                       render_kw={'placeholder': 'contact@company.com'})
    
    website = StringField('Website', 
                         validators=[Optional(), URL(), Length(max=200)],
                         render_kw={'placeholder': 'https://www.company.com'})


@organization_bp.route('/')
@login_required
def index():
    """Display organization details."""
    # Get the current organization (assuming single-tenant for now)
    # In multi-tenant setup, you'd filter by current user's organization
    organization = Organization.query.first()
    
    if not organization:
        # Create a default organization if none exists
        organization = Organization(
            name="Your Organization",
            language="en"
        )
        db.session.add(organization)
        db.session.commit()
        flash('Default organization created. Please update your information.', 'info')
    
    return render_template('organization/index.html', 
                         organization=organization)


@organization_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit organization information."""
    organization = Organization.query.first()
    
    if not organization:
        organization = Organization(name="Your Organization", language="en")
        db.session.add(organization)
        db.session.commit()
    
    form = OrganizationForm(obj=organization)
    
    if form.validate_on_submit():
        try:
            # Update organization with form data
            form.populate_obj(organization)
            db.session.commit()
            
            flash('Organization information updated successfully!', 'success')
            return redirect(url_for('organization.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating organization: {str(e)}', 'danger')
    
    return render_template('organization/edit.html', 
                         form=form, 
                         organization=organization)


@organization_bp.route('/settings')
@login_required
def settings():
    """Organization settings page (placeholder)."""
    flash('Settings page is under development.', 'info')
    return redirect(url_for('organization.index'))


@organization_bp.route('/backup')
@login_required
def backup():
    """Organization data backup (placeholder)."""
    flash('Backup functionality is under development.', 'info')
    return redirect(url_for('organization.index'))


# Helper functions for templates
@organization_bp.app_template_global()
def get_organization():
    """Template global function to get current organization."""
    return Organization.query.first()


# Error handlers
@organization_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors within organization blueprint."""
    flash('The requested page was not found.', 'warning')
    return redirect(url_for('organization.index'))


@organization_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within organization blueprint."""
    db.session.rollback()
    flash('An internal error occurred. Please try again.', 'danger')
    return redirect(url_for('organization.index'))