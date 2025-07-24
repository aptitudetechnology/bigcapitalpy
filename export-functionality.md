# Export Functionality (PDF, Excel, CSV)
## Description
Export data and reports in PDF, Excel, and CSV formats.

## Status
Not yet fully implemented for all reports.

## Claude Implementation Instructions

**Goal:** Implement export for all major entities and reports in PDF, Excel, and CSV.
**Instructions for Claude:**
Start by generating the UI Jinja2 templates for export buttons and pages, then work backwards to implement the backend code and endpoints. Follow the order of sections below.

**Scope:**
- Users can export data from all major reports and lists.
- Admins can export organization-wide data (optional).

### 1. Jinja2 Templates
- Add export buttons (PDF, Excel, CSV) to all relevant list/detail pages.

### 2. Python Backend (Flask)
- Add export endpoints to each relevant blueprint (e.g., `/export/pdf`, `/export/csv`).
- Use Pandas for CSV/Excel export (`df.to_csv`, `df.to_excel`).
- Use `WeasyPrint` or `xhtml2pdf` for PDF export from HTML templates.
- Ensure proper content-disposition headers for downloads.

### 3. JavaScript
- Optionally use JS to trigger downloads or show export progress.

### 4. Libraries to Use
- **Pandas**: For CSV/Excel export.
- **WeasyPrint** or **xhtml2pdf**: For PDF export.
- **Flask**: For routing.

### 5. Testing
- Add tests to verify export endpoints and file contents.

---
**Tip:** Reuse existing report queries for export endpoints to ensure consistency.

**Important:** Do not generate any CSS. Use Bootstrap classes only for styling.

## Description
Export data and reports in PDF, Excel, and CSV formats.

## Status
Not yet fully implemented for all reports.

## Claude Implementation Instructions

**Goal:** Implement export for all major entities and reports in PDF, Excel, and CSV.

### 1. Jinja2 Templates
- Add export buttons (PDF, Excel, CSV) to all relevant list/detail pages.

### 2. Python Backend (Flask)
- Add export endpoints to each relevant blueprint (e.g., `/export/pdf`, `/export/csv`).
- Use Pandas for CSV/Excel export (`df.to_csv`, `df.to_excel`).
- Use `WeasyPrint` or `xhtml2pdf` for PDF export from HTML templates.
- Ensure proper content-disposition headers for downloads.

### 3. JavaScript
- Optionally use JS to trigger downloads or show export progress.

### 4. Libraries to Use
- **Pandas**: For CSV/Excel export.
- **WeasyPrint** or **xhtml2pdf**: For PDF export.
- **Flask**: For routing.

### 5. Testing
- Add tests to verify export endpoints and file contents.

---
**Tip:** Reuse existing report queries for export endpoints to ensure consistency.
