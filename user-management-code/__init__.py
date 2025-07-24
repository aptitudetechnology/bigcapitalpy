from flask import Blueprint

user_bp = Blueprint('user', __name__, url_prefix='/system/user')

from . import routes