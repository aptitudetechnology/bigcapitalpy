from flask import Blueprint, render_template
custom_bp = Blueprint('custom', __name__)

# Custom Report Builder route (for reports.custom_report_builder endpoint)
@custom_bp.route('/custom-report-builder')
def custom_report_builder():
    # TODO: Replace with real data and template
    return render_template('reports/custom-advanced/custom.html')
