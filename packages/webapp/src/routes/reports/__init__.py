# Removed top-level blueprint imports to prevent circular dependencies.
# from .tax import tax_bp
# from .sales import sales_bp
# from .financial import financial_bp
# from .expenses import expenses_bp
# from .utils import utils_bp


def register_reports_blueprints(app):
    """
    Registers all report-related blueprints with the Flask application.
    Imports are placed inside this function to prevent circular import issues.
    """
    # Import blueprints here to avoid circular dependencies at module load time
    from .tax import tax_bp
    from .sales import sales_bp
    from .financial import financial_bp
    from .expenses import expenses_bp
    # If utils_bp is ever used as a blueprint, uncomment and import it here
    # from .utils import utils_bp 

    app.register_blueprint(tax_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(financial_bp)
    app.register_blueprint(expenses_bp)
    # app.register_blueprint(utils_bp) # Uncomment if utils_bp is a blueprint to be registered
