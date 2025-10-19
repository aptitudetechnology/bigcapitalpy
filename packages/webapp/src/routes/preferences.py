from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime

preferences_bp = Blueprint('preferences', __name__, url_prefix='/preferences')

@preferences_bp.route('/')
@login_required
def index():
    return render_template('preferences/index.html', current_year=datetime.now().year)
