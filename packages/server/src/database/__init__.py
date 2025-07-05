"""
Database configuration and initialization for BigCapitalPy
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize database instance
db = SQLAlchemy()
migrate = Migrate()
