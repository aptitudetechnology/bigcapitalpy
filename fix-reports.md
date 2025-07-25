# BigCapitalPy Flask TemplateNotFound Investigation Report

## Executive Summary

**Issue:**  
Most financial report routes (13+) fail with `TemplateNotFound`, while only Invoice Summary and Tax Summary work. This is a systemic template discovery or configuration issue, not isolated missing files.

**Root Cause Analysis:**  
- The working reports likely use a different template path, directory, or blueprint configuration than the failing ones.
- There may be a mismatch between the expected template directory structure and the actual file locations, or a misconfiguration in Flask's `template_folder` or blueprint registration.

**Recommended Solution Approach:**  
- Audit and align the template directory structure and blueprint `template_folder` settings.
- Ensure all `render_template()` calls use the correct relative paths.
- Use the working reports as a reference for fixing failing ones.

---

## Findings

### 1. Systemic Template Issue

- **Scope:** 13+ reports fail, only 2 work.
- **Pattern:** Invoice Summary and Tax Summary succeed, suggesting their templates are in the correct location or use a different loading mechanism.
- **Implication:** The issue is likely with template discovery/configuration, not individual missing files.

### 2. Template Directory Structure

- **Expected:**  
  ```
  bigcapitalpy/packages/webapp/src/templates/
    reports/
      financial/
        profit_loss.html
        balance_sheet.html
        cash_flow.html
        trial_balance.html
        general_ledger.html
      sales/
        sales_summary.html
        customer_aging.html
        invoice_summary.html
      expenses/
        expense_summary.html
        vendor_aging.html
        purchase_summary.html
      tax/
        australian_gst_bas.html
        tax_codes_report.html
        tax_summary.html
      custom/
        custom_report_builder.html
        profitability_analysis.html
        executive_dashboard.html
  ```
- **Actual:**  
  - Invoice Summary and Tax Summary templates exist and are found.
  - Other templates may be missing, misnamed, or in the wrong directory.
  - Possible that some blueprints have their own `template_folder` set, causing Flask to look in the wrong place.

### 3. Route Handler Inconsistencies

- **Working Example (Invoice Summary):**
  ```python
  @sales_bp.route('/invoice-summary')
  def invoice_summary():
      return render_template('reports/sales/invoice_summary.html', ...)
  ```
- **Failing Example (Profit & Loss):**
  ```python
  @financial_bp.route('/profit-loss')
  def profit_loss():
      return render_template('reports/financial/profit_loss.html', ...)
  ```
- **Observation:**  
  - Both use `render_template()` with a path under `reports/`, but only some succeed.
  - If blueprints are registered with a custom `template_folder`, Flask may not find templates in the default location.

---

## Recommendations

### 1. Immediate Mass Fix

- **Audit the template directory:**  
  - Ensure all expected templates exist at the correct paths (see structure above).
  - If missing, create stubs for each failing report.
- **Check blueprint registration:**  
  - If any blueprint is registered with a `template_folder`, ensure it matches the actual directory structure.
- **Align all `render_template()` calls:**  
  - Use the same pattern as the working reports.

### 2. Root Cause Resolution

- **Standardize template loading:**  
  - Remove unnecessary `template_folder` arguments from blueprints unless needed.
  - Use a single, consistent template directory for all reports.
- **Implement template inheritance:**  
  - Ensure all report templates extend a common `base.html` or `reports/base.html`.
- **Add template existence validation:**  
  - During development, add a check to verify all expected templates exist.

### 3. Prevention Measures

- **Automated testing:**  
  - Add tests to hit every report route and check for 200 OK and correct template rendering.
- **Startup validation:**  
  - On app startup, log missing templates for all known report routes.
- **Documentation:**  
  - Document the expected template structure and naming conventions.

---

## Implementation Steps

### 1. Immediate Triage

- **Find all .html templates:**
  ```bash
  find packages/webapp/src/templates -name '*.html'
  ```
- **Copy working template structure:**  
  - Use the directory and naming pattern from Invoice Summary and Tax Summary for all other reports.
- **Test one failing report:**  
  - Create `profit_loss.html` in `templates/reports/financial/` and verify the route works.

### 2. Mass Template Recovery

- **Create missing directories/files:**  
  - For each failing report, create the expected directory and a basic template file.
- **Update route handlers if needed:**  
  - Ensure all `render_template()` calls use the correct path.

### 3. Configuration Standardization

- **Blueprint registration:**  
  - Register all blueprints without a custom `template_folder` unless absolutely necessary.
- **Centralize template path logic:**  
  - Use a helper or consistent pattern for all report templates.

### 4. Verification

- **Test all report routes:**  
  - Systematically visit each report URL and verify the template loads.
- **Check inheritance:**  
  - Ensure all templates extend the correct base.

---

## Code Examples

**Working Route Handler:**
```python
@sales_bp.route('/invoice-summary')
def invoice_summary():
    return render_template('reports/sales/invoice_summary.html', ...)
```

**Blueprint Registration:**
```python
# Good: No template_folder, uses default
sales_bp = Blueprint('sales', __name__)
```

**Directory Structure Command:**
```bash
find bigcapitalpy/packages/webapp/src/templates/reports -type f
```

**Template Stub Example:**
```html
<!-- bigcapitalpy/packages/webapp/src/templates/reports/financial/profit_loss.html -->
{% extends "base.html" %}
{% block content %}
<h1>Profit & Loss Statement</h1>
<p>This is a placeholder for the Profit & Loss report.</p>
{% endblock %}
```

---

## Additional Analysis Points

- This is part of a larger financial reporting module.
- Data for each report should be passed as context in `render_template`.
- Bootstrap is used for styling; ensure new templates use the same base.

---

## Summary Table: Template Path Audit

| Report Name                | Expected Template Path                        | Exists? | Notes                |
|----------------------------|----------------------------------------------|---------|----------------------|
| Profit & Loss Statement    | reports/financial/profit_loss.html           | ?       | Failing              |
| Balance Sheet              | reports/financial/balance_sheet.html         | ?       | Failing              |
| Cash Flow Statement        | reports/financial/cash_flow.html             | ?       | Failing              |
| Sales Summary              | reports/sales/sales_summary.html             | ?       | Failing              |
| Customer Aging Report      | reports/sales/customer_aging.html            | ?       | Failing              |
| Invoice Summary            | reports/sales/invoice_summary.html           | Yes     | Working              |
| Expense Summary            | reports/expenses/expense_summary.html        | ?       | Failing              |
| Vendor Aging Report        | reports/expenses/vendor_aging.html           | ?       | Failing              |
| Purchase Summary           | reports/expenses/purchase_summary.html       | ?       | Failing              |
| Australian GST BAS Report  | reports/tax/australian_gst_bas.html          | ?       | Failing              |
| Tax Codes Configuration    | reports/tax/tax_codes_report.html            | ?       | Failing              |
| Tax Summary                | reports/tax/tax_summary.html                 | Yes     | Working              |
| General Ledger             | reports/financial/general_ledger.html        | ?       | Failing              |
| Trial Balance              | reports/financial/trial_balance.html         | ?       | Failing              |
| Custom Report Builder      | reports/custom/custom_report_builder.html     | ?       | Failing              |
| Profitability Analysis     | reports/custom/profitability_analysis.html   | ?       | Failing              |
| Executive Dashboard        | reports/custom/executive_dashboard.html      | ?       | Failing              |

---

## Action Plan

1. **Audit and create missing templates in the correct directories.**
2. **Align all blueprint and route handler template paths to the working pattern.**
3. **Test each report route after creating the template.**
4. **Standardize and document the template structure for future development.**

---

If you want, I can generate stubs for all missing templates and provide a shell script or code to automate this process. Let me know how you'd like to proceed!
