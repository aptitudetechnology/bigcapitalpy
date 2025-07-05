"""
BigCapitalPy REST API
Main API package initialization
"""

from .v1 import register_api_blueprints

__version__ = '1.0.0'
__all__ = ['register_api_blueprints']
