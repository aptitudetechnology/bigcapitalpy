from .tax import tax_bp
from .sales import sales_bp
from .financial import financial_bp
from .expenses import expenses_bp
#from .utils import utils_bp


def register_reports_blueprints(app):
    app.register_blueprint(tax_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(financial_bp)
    app.register_blueprint(expenses_bp)
  #  app.register_blueprint(utils_bp)
