import os

# Define the base directory for your web application templates
# Assuming this script is run from the 'bigcapitalpy' root directory
BASE_TEMPLATES_DIR = 'packages/webapp/src/templates'

# List of files to create with their titles
# The key is the path relative to BASE_TEMPLATES_DIR, and the value is the title.
files_to_create = {
    'expenses/index.html': 'Expenses List',
    'reports/expense_summary.html': 'Expense Summary Report',
    'reports/vendor_aging.html': 'Vendor Aging Report',
    'reports/purchase_summary.html': 'Purchase Summary Report',
    'reports/custom_report_builder.html': 'Custom Report Builder',
    'reports/profitability_analysis.html': 'Profitability Analysis Report',
    'reports/executive_dashboard.html': 'Executive Dashboard',
    'reports/australian_gst_bas.html': 'Australian GST BAS Report',
    'reports/tax_codes_report.html': 'Tax Codes Configuration',
    'reports/tax_summary.html': 'Tax Summary Report',
    'reports/sales_summary.html': 'Sales Summary Report',
    'reports/customer_aging.html': 'Customer Aging Report',
    'reports/invoice_summary.html': 'Invoice Summary Report',
    'accounts/index.html': 'Chart of Accounts',
    # Add any other missing templates here if you identify more
    # For example, if 'financial/index.html' or 'financial/banking.html' etc. were missing
    # 'financial/index.html': 'Financial Dashboard',
    # 'financial/banking.html': 'Banking Overview',
    # 'financial/manual_journals.html': 'Manual Journals',
    # 'financial/reconciliation.html': 'Bank Reconciliation',
    # 'financial/cash_flow.html': 'Cash Flow',
    # 'customers/new.html': 'New Customer', # If you need form templates
    # 'customers/show.html': 'Customer Details',
    # 'customers/edit.html': 'Edit Customer',
    # 'items/new.html': 'New Item',
    # 'items/show.html': 'Item Details',
    # 'items/edit.html': 'Edit Item',
}

def create_placeholder_template(filepath, title):
    """
    Creates a placeholder HTML file with basic Jinja2 extends and title blocks.
    """
    full_path = os.path.join(BASE_TEMPLATES_DIR, filepath)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    content = f"""{{% extends "base.html" %}}

{{% block title %}}{title} - BigCapitalPy{{% endblock %}}

{{% block content %}}
<div class="container-fluid">
    <h1 class="h3 mb-4 text-gray-800">{title}</h1>
    <p>This is the placeholder for the {title} page.</p>
    {# Add specific content for this page here later #}
</div>
{{% endblock %}}
"""
    with open(full_path, 'w') as f:
        f.write(content)
    print(f"Created: {full_path}")

if __name__ == "__main__":
    print("Starting creation of placeholder HTML templates...")
    for filepath, title in files_to_create.items():
        create_placeholder_template(filepath, title)
    print("\nAll specified placeholder HTML templates created successfully!")
    print("Remember to restart your Flask development server after this.")

