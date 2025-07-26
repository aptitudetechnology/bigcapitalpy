from flask import Blueprint, render_template
from flask_login import login_required, current_user  # Add current_user

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

@backup_bp.route('/')
@login_required
def index():
    # Placeholder context for now
    return render_template('backup/index.html', 
                           last_backup_timestamp=None,
                            previous_backups=None,
                            enable_scheduled_backups=False,
                            user=current_user)  
