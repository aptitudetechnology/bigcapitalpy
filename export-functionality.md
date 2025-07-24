# Export Functionality (PDF, Excel, CSV)

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
