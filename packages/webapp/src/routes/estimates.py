from flask import Blueprint, render_template
from flask_login import login_required

estimates_bp = Blueprint('estimates', __name__, url_prefix='/estimates')

@estimates_bp.route('/')
@login_required
def index():
    return render_template('estimates/index.html')