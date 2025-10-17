#!/usr/bin/env python3
"""
Simple migration runner for BigCapitalPy BankAccount model
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
import os

def run_migration():
    """Run the BankAccount migration"""

    # Create minimal Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bigcapitalpy.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    # Import the BankAccount model
    from packages.server.src.models import BankAccount

    with app.app_context():
        # Create all tables (including the new BankAccount)
        db.create_all()
        print("✅ BankAccount table created successfully")
        print("📍 Database:", app.config['SQLALCHEMY_DATABASE_URI'])

if __name__ == '__main__':
    run_migration()