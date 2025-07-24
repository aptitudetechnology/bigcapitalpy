chris@simple:~/bigcapitalpy/scripts$ python3 test_links.py 
Attempting to log in to http://simple.local:5000/auth/login...
Using Email: admin@bigcapitalpy.com
Using Password: admin123
CSRF token obtained: IjM4MDNiYW...
Login POST request completed. Final URL: http://simple.local:5000/
Login successful. Starting crawl...
Crawling: http://simple.local:5000
Crawling: http://simple.local:5000/
Crawling: http://simple.local:5000/customers/
Crawling: http://simple.local:5000/vendors/
Crawling: http://simple.local:5000/items/
Crawling: http://simple.local:5000/invoices/
Crawling: http://simple.local:5000/payments/
Crawling: http://simple.local:5000/accounts/
Crawling: http://simple.local:5000/financial/
Crawling: http://simple.local:5000/financial/banking
Crawling: http://simple.local:5000/financial/manual-journals
Crawling: http://simple.local:5000/financial/reconciliation
Crawling: http://simple.local:5000/financial/cash-flow
Crawling: http://simple.local:5000/reports/
Crawling: http://simple.local:5000/auth/logout
Crawling: http://simple.local:5000/auth/register
Crawling: http://simple.local:5000/auth/login
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
Crawling: http://simple.local:5000/reports/custom
Crawling: http://simple.local:5000/reports/profitability
Crawling: http://simple.local:5000/reports/dashboard
Crawling: http://simple.local:5000/financial/cash-flow?format=pdf
Crawling: http://simple.local:5000/financial/cash-flow?format=excel
Crawling: http://simple.local:5000/financial/cash-flow?format=csv
Crawling: http://simple.local:5000/accounts/new
Crawling: http://simple.local:5000/financial/manual-journals/create
Crawling: http://simple.local:5000/accounts/?type=asset
Crawling: http://simple.local:5000/accounts/new?type=asset
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

Summary: Checked 48 pages
Found 0 broken links
Found 161 dummy/placeholder links
Found 52 text/URL mismatches

--- DUMMY/PLACEHOLDER LINKS (161) ---
🔗 Page: http://simple.local:5000/invoices/
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/payments/
   Link: 'Credit Notes' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/
   Link: 'Credit Notes' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/
   Link: 'Credit Notes' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/banking
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/banking
   Link: 'Credit Notes' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals
   Link: 'Credit Notes' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/reconciliation
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/reconciliation
   Link: 'Credit Notes' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow
   Link: 'Credit Notes' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Credit Notes' -> #
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

🔗 Page: http://simple.local:5000/auth/logout
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/auth/login
   Link: 'Forgot Password?' -> #
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

🔗 Page: http://simple.local:5000/reports/profit-loss
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/balance-sheet
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/cash-flow
   Link: 'Forgot Password?' -> #
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

🔗 Page: http://simple.local:5000/reports/expense-summary
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/vendor-aging
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/purchase-summary
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

🔗 Page: http://simple.local:5000/reports/general-ledger
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/trial-balance
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/custom
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/profitability
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/dashboard
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/reports/
   Link: 'Clear History' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow?format=pdf
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow?format=excel
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/cash-flow?format=csv
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals/create
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/?type=asset
   Link: 'Forgot Password?' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/reconciliation
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/reconciliation
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/reconciliation
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/reconciliation
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/reconciliation
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/reconciliation
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/reconciliation
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/manual-journals
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/banking
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/banking
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/banking
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/banking
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/banking
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/banking
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/banking
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/financial/
   Link: 'Help' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/
   Link: 'New invoice created' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/
   Link: 'Payment overdue' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/
   Link: 'Report generated' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/
   Link: 'View all notifications' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/
   Link: 'Profile' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/
   Link: 'Settings' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/accounts/
   Link: 'Help' -> #
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
   Link: 'Credit Notes' -> #
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
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/items/
   Link: 'Credit Notes' -> #
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
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/vendors/
   Link: 'Credit Notes' -> #
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
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/customers/
   Link: 'Credit Notes' -> #
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
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000/
   Link: 'Credit Notes' -> #
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
   Link: 'Estimates' -> #
   Issue: Hash-only link (no dropdown functionality)

🔗 Page: http://simple.local:5000
   Link: 'Credit Notes' -> #
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


--- TEXT/URL MISMATCHES (52) ---
⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Sales & Inventory' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'sales' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Sales' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'sales' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Sales & Inventory' -> http://simple.local:5000/reports/
   Issue: Text suggests 'sales' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Sales' -> http://simple.local:5000/reports/
   Issue: Text suggests 'sales' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Accounting' -> http://simple.local:5000/reports/
   Issue: Text suggests 'accounting' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'System' -> http://simple.local:5000/reports/
   Issue: Text suggests 'system' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Organization' -> http://simple.local:5000/reports/
   Issue: Text suggests 'organization' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Users & Permissions' -> http://simple.local:5000/reports/
   Issue: Text suggests 'permissions' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Backup & Restore' -> http://simple.local:5000/reports/
   Issue: Text suggests 'backup' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/auth/logout
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/auth/login
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/profit-loss
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/balance-sheet
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/cash-flow
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/sales-summary
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/customer-aging
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/invoice-summary
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/expense-summary
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/vendor-aging
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/
   Link: 'Purchase SummaryPurchase orders and spending analysis' -> http://simple.local:5000/reports/purchase-summary
   Issue: Text suggests 'orders' but URL suggests 'reports'

⚠️  Page: http://simple.local:5000/reports/purchase-summary
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/australian-gst-bas
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/tax-codes
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/tax-summary
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/general-ledger
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/trial-balance
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/custom
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/profitability
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/reports/dashboard
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/financial/cash-flow?format=pdf
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/financial/cash-flow?format=excel
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/financial/cash-flow?format=csv
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/financial/manual-journals/create
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/accounts/?type=asset
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/payments/create
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Accounting' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'accounting' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'System' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'system' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Organization' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'organization' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Users & Permissions' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'permissions' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/invoices/
   Link: 'Backup & Restore' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'backup' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000/invoices/create
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/items/new
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/vendors/new
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/vendors/1
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/vendors/1/edit
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

⚠️  Page: http://simple.local:5000/customers/new
   Link: 'Create Account' -> http://simple.local:5000/auth/register
   Issue: Text suggests 'create' but URL suggests 'register'

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
   Link: 'View All' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'view' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000
   Link: 'Create InvoiceBill your customers' -> http://simple.local:5000/invoices/
   Issue: Text suggests 'create' but URL suggests 'invoices'

⚠️  Page: http://simple.local:5000
   Link: 'View ReportsFinancial insights' -> http://simple.local:5000/reports/
   Issue: Text suggests 'view' but URL suggests 'reports'

