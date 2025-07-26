 python3 scripts/test_links.py 
Attempting to log in to http://simple.local:5000/auth/login...
Using Email: admin@bigcapitalpy.com
Using Password: admin123
CSRF token obtained: IjY4Njc5NW...
Login POST request completed. Final URL: http://simple.local:5000/
Login successful. Starting crawl...
Crawling: http://simple.local:5000
Crawling: http://simple.local:5000/
Crawling: http://simple.local:5000/customers/
Crawling: http://simple.local:5000/vendors/
Crawling: http://simple.local:5000/items/
Crawling: http://simple.local:5000/invoices/
Crawling: http://simple.local:5000/estimates/
  ⚠️  Rendering error detected: Jinja2 Template Error
Crawling: http://simple.local:5000/payments/
Crawling: http://simple.local:5000/accounts/
  ⚠️  Rendering error detected: Jinja2 Template Error
Crawling: http://simple.local:5000/reports/
Crawling: http://simple.local:5000/organization/
Crawling: http://simple.local:5000/system/user/settings
Crawling: http://simple.local:5000/system/user/profile
Crawling: http://simple.local:5000/preferences/
  ⚠️  Rendering error detected: Jinja2 Template Error
Crawling: http://simple.local:5000/backup/
Crawling: http://simple.local:5000/auth/logout
Crawling: http://simple.local:5000/auth/register
Crawling: http://simple.local:5000/auth/login
Crawling: http://simple.local:5000/system/user/change-password
Crawling: http://simple.local:5000/system/user/settings/edit
Crawling: http://simple.local:5000/organization/edit
Crawling: http://simple.local:5000/organization/settings
Crawling: http://simple.local:5000/organization/backup
Crawling: http://simple.local:5000/reports/profit-loss
Crawling: http://simple.local:5000/reports/balance-sheet
Crawling: http://simple.local:5000/reports/cash-flow
Crawling: http://simple.local:5000/reports/sales-summary
Crawling: http://simple.local:5000/reports/customer-aging
Crawling: http://simple.local:5000/reports/invoice-summary
Crawling: http://simple.local:5000/reports/expense-summary
Crawling: http://simple.local:5000/reports/vendor-aging
Crawling: http://simple.local:5000/reports/purchase-summary
Crawling: http://simple.local:5000/reports/australian-gst-bas
Crawling: http://simple.local:5000/reports/tax-codes
Crawling: http://simple.local:5000/reports/tax-summary
Crawling: http://simple.local:5000/reports/general-ledger
Crawling: http://simple.local:5000/reports/trial-balance
Crawling: http://simple.local:5000/reports/custom-report-builder
Crawling: http://simple.local:5000/reports/profitability-analysis
  ⚠️  Rendering error detected: Jinja2 Template Error
Crawling: http://simple.local:5000/reports/executive-dashboard
  ⚠️  Rendering error detected: Jinja2 Template Error
Crawling: http://simple.local:5000/payments/create
Crawling: http://simple.local:5000/invoices/create
Crawling: http://simple.local:5000/items/new
Crawling: http://simple.local:5000/vendors/new
Crawling: http://simple.local:5000/vendors/1
Crawling: http://simple.local:5000/vendors/1/edit
Crawling: http://simple.local:5000/customers/new

============================================================
CRAWL RESULTS
============================================================

Summary: Checked 47 pages
Found 0 broken links
Found 124 dummy/placeholder links
Found 75 text/URL mismatches
Found 5 rendering/template errors

--- RENDERING/TEMPLATE ERRORS (5) ---
🔥 http://simple.local:5000/estimates/
   Status: HTTP 500
   Type: Jinja2 Template Error
   Error: jinja2.exceptions.TemplateNotFound: estimates/index.html

🔥 http://simple.local:5000/accounts/
   Status: HTTP 500
   Type: Jinja2 Template Error
   Error: UndefinedError: &#39;jinja2.runtime.TemplateReference object&#39; has no attribute &#39;render_account_tree&#39;

🔥 http://simple.local:5000/preferences/
   Status: HTTP 500
   Type: Jinja2 Template Error
   Error: TemplateAssertionError: No filter named &#39;strftime&#39;.

🔥 http://simple.local:5000/reports/profitability-analysis
   Status: HTTP 500
   Type: Jinja2 Template Error
   Error: jinja2.exceptions.TemplateNotFound: reports/profitability_analysis.html

🔥 http://simple.local:5000/reports/executive-dashboard
   Status: HTTP 500
   Type: Jinja2 Template Error
   Error: jinja2.exceptions.TemplateNotFound: reports/executive_dashboard.html


--- DUMMY/PLACEHOLDER LINKS (124) ---
🔗 Page: http://simple.local:5000/payments/
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/settings
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/profile
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/auth/logout
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/auth/login
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'Google DriveConnect your Google Drive account' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'DropboxConnect your Dropbox account' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'AWS S3Configure AWS S3 bucket' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/backup/
   Link: 'View Audit Log' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/profile
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/profile
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/profile
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/profile
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/profile
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/profile
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/profile
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/change-password
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/settings
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/settings
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/settings
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/settings
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/settings
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/settings
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/settings
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/system/user/settings/edit
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/edit
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/settings
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/organization/backup
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'PDF' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Excel' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'CSV' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/sales-summary
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/customer-aging
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/invoice-summary
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/australian-gst-bas
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/tax-codes
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/tax-summary
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Clear History' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/create
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/invoices/
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/invoices/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/invoices/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/invoices/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/invoices/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/invoices/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/invoices/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/invoices/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/invoices/create
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/new
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/new
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/1
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/1/edit
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/new
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000
   Link: 'Credit Notes (Coming Soon)' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)


--- TEXT/URL MISMATCHES (75) ---
⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Sales & Inventory' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'inventory' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Sales' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'sales' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Sales & Inventory' -> http://simple.local:5000/reports/
   Issue: Text suggests 'inventory' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Sales' -> http://simple.local:5000/reports/
   Issue: Text suggests 'sales' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Accounting' -> http://simple.local:5000/reports/
   Issue: Text suggests 'accounting' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'System' -> http://simple.local:5000/reports/
   Issue: Text suggests 'system' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/organization/
   Link: 'Sales & Inventory' -> http://simple.local:5000/organization/
   Issue: Text suggests 'inventory' but URL suggests 'organization'

⚠️  Page: http://simple.local:5000/organization/
   Link: 'Sales' -> http://simple.local:5000/organization/
   Issue: Text suggests 'sales' but URL suggests 'organization'

⚠️  Page: http://simple.local:5000/organization/
   Link: 'Accounting' -> http://simple.local:5000/organization/
   Issue: Text suggests 'accounting' but URL suggests 'organization'

⚠️  Page: http://simple.local:5000/organization/
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/organization/
   Link: 'System' -> http://simple.local:5000/organization/
   Issue: Text suggests 'system' but URL suggests 'organization'

⚠️  Page: http://simple.local:5000/organization/
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/system/user/settings
   Link: 'Sales & Inventory' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'inventory' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/system/user/settings
   Link: 'Sales' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'sales' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/system/user/settings
   Link: 'Accounting' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'accounting' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/system/user/settings
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/system/user/settings
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/system/user/profile
   Link: 'Sales & Inventory' -> http://simple.local:5000/system/user/profile
   Issue: Text suggests 'inventory' but URL suggests 'system'

⚠️  Page: http://simple.local:5000/system/user/profile
   Link: 'Sales' -> http://simple.local:5000/system/user/profile
   Issue: Text suggests 'sales' but URL suggests 'system'

⚠️  Page: http://simple.local:5000/system/user/profile
   Link: 'Accounting' -> http://simple.local:5000/system/user/profile
   Issue: Text suggests 'accounting' but URL suggests 'system'

⚠️  Page: http://simple.local:5000/system/user/profile
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/system/user/profile
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/backup/
   Link: 'Sales & Inventory' -> http://simple.local:5000/backup/
   Issue: Text suggests 'inventory' but URL suggests 'backup'

⚠️  Page: http://simple.local:5000/backup/
   Link: 'Sales' -> http://simple.local:5000/backup/
   Issue: Text suggests 'sales' but URL suggests 'backup'

⚠️  Page: http://simple.local:5000/backup/
   Link: 'Accounting' -> http://simple.local:5000/backup/
   Issue: Text suggests 'accounting' but URL suggests 'backup'

⚠️  Page: http://simple.local:5000/backup/
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/backup/
   Link: 'System' -> http://simple.local:5000/backup/
   Issue: Text suggests 'system' but URL suggests 'backup'

⚠️  Page: http://simple.local:5000/backup/
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/auth/logout
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/auth/login
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/system/user/profile
   Link: 'Edit Profile' -> http://simple.local:5000/system/user/profile
   Issue: Text suggests 'edit' but URL suggests 'system'

⚠️  Page: http://simple.local:5000/system/user/change-password
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/system/user/settings/edit
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/system/user/settings
   Link: 'View Profile' -> http://simple.local:5000/system/user/profile
   Issue: Text suggests 'view' but URL suggests 'system'

⚠️  Page: http://simple.local:5000/organization/edit
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/organization/settings
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/organization/backup
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/reports/sales-summary
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/customer-aging
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/invoice-summary
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Purchase SummaryPurchase orders and spending analysis' -> http://simple.local:5000/reports/purchase-summary
   Issue: Text suggests 'orders' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/australian-gst-bas
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/tax-codes
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/tax-summary
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/payments/
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/payments/
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/payments/create
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Accounting' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'accounting' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'System' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'system' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/invoices/create
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/items/
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/items/
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/items/new
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/vendors/
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/vendors/
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/vendors/new
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/vendors/1
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/vendors/1/edit
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/customers/
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/customers/
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/customers/new
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000/
   Link: 'View All' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'view' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/
   Link: 'Create InvoiceBill your customers' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'create' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/
   Link: 'View ReportsFinancial insights' -> http://simple.local:5000/reports/
   Issue: Text suggests 'view' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000
   Link: 'Financial Dashboard' -> http://simple.local:5000/reports/
   Issue: Text suggests 'dashboard' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000
   Link: 'Users & Permissions' -> http://simple.local:5000/system/user/settings
   Issue: Text suggests 'permissions' but URL suggests 'settings'

⚠️  Page: http://simple.local:5000
   Link: 'View All' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'view' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000
   Link: 'Create InvoiceBill your customers' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'create' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000
   Link: 'View ReportsFinancial insights' -> http://simple.local:5000/reports/
   Issue: Text suggests 'view' but URL suggests 'reports'
