# BigCapitalPy Missing Functionality Report

**Last verified: 2026-08-02** · Branch `development` @ `da35365ca`
Comparison base: the original BigCapital (TypeScript/NestJS/React), which lives alongside the port in
this repo at `packages/server/src/modules/**` (76 NestJS modules) and
`packages/webapp/src/containers/**` + `routes/dashboard.tsx` (~95 React routes).

> **Companion document:** [OUTSTANDING_WORK.md](OUTSTANDING_WORK.md) carries the file-and-line-level
> defect list (broken `url_for` targets, mock implementations, security gaps) and a suggested work
> order. This report is the feature-parity ledger.

> **Revision note:** this file previously contained two concatenated reports dated 2025-07-05 and
> 2025-07-25. Both had drifted badly — six modules they listed as missing have since been built, and
> several marked "✅ complete" are not. It has been rewritten from a fresh source audit.

---

## Implementation Status Overview

### ✅ Implemented and backed by real database work

- Customers, Vendors, Items, Item Categories — full CRUD
- **Sales invoices** — full lifecycle incl. GL posting and mark-paid
- **Sale estimates** — incl. approve/reject and convert-to-invoice
- **Sale receipts** — create/view/close/delete
- **Bills** — full lifecycle incl. approve, pay and record-payment
- **Credit notes & vendor credits** — incl. open and apply-to-document
- **Expenses** — full lifecycle incl. approve
- **Payments received** — with allocation to invoices
- Manual journal entries; bank transaction CSV import; bank reconciliation with auto-match
- Financial reports: Balance Sheet, P&L, Trial Balance, General Ledger, Cash Flow, AR aging
- Australian GST/BAS reporting and tax codes — **a deliberate addition the original lacks**
- Double-entry posting: `JournalEntry`/`JournalLineItem` rows are written by invoices, bills,
  payments, expenses, credit notes, vendor credits and sale receipts
- REST API v1 — 84 endpoints across 16 blueprints
- Docker environment; SQLAlchemy models for all of the above

### 🟡 Partially implemented

- **Import/Export** — CSV import and export for customers, vendors and items only (3 resources vs
  ~15 importable resources in the original)
- **Authentication** — login/logout work; **registration is a no-op stub** and password reset sends
  no mail
- **Tax** — AU BAS complete; no sales-tax liability summary, no other jurisdictions
- **Multi-tenancy** — single database with an `organization_id` column, scoped per query rather than
  centrally enforced. The original gives each tenant its own database.
- **Preferences/Settings** — pages render but several handlers flash success and save nothing

### ⚠️ Reported complete previously, but is not

These were marked ✅ in the prior revision. They are not.

| Claim | Reality |
|---|---|
| "Chart of Accounts (CRUD operations)" | Was **entirely mock** — zero `.query.` calls, hardcoded seed list, discarded input. **Rewritten 2026-08-02** against the `Account` model: real CRUD, balances derived from journal lines, parent/child tree with cycle prevention, delete guards, org scoping. Now genuinely implemented. |
| "Aging Reports — AP aging complete" | Vendor aging is a data-less stub — `# TODO: Replace with real data` in [reports/expenses.py](packages/webapp/src/routes/reports/expenses.py) |
| "Core Authentication & User Management" | No registration, no user list, no invites, no roles |
| "Financial reporting engine complete" | 7 of the original's 20 reports are ported — see §4 |
| "Production-ready for basic accounting operations" | Contradicted by the README's own PRE-ALPHA warning. The boot-blocking and 500-level defects have since been cleared, but the platform gaps below remain; see [OUTSTANDING_WORK.md](OUTSTANDING_WORK.md) |

---

## 1. Core Business Modules

Largely **done**. The prior revision's ❌ marks on estimates, sale receipts, bills, bill payments,
credit notes and vendor credits are obsolete. Remaining gaps within these modules:

- ❌ No edit route for sale receipts, credit notes or vendor credits (create/view/delete only)
- ❌ Purchase orders — no PO module, no three-way matching
- ❌ Recurring invoices; no approval hierarchies beyond a single `approve` action
- ❌ Invoice/estimate "send" changes status only — **no email is sent**
  ([invoices.py:391](packages/webapp/src/routes/invoices.py#L391) `# TODO: Send email to customer`)
- ❌ Check printing, payment scheduling, electronic payment execution

## 2. Advanced Financial Features

- ❌ **Multi-currency** — `currency` is a bare `String(3)` on 11 models with **no exchange-rate table
  and no revaluation**. Realized/unrealized gain-loss reporting is impossible until this lands.
- ❌ **Inventory costing** (`InventoryCost`) — no FIFO/average cost layers, so COGS is not computed
- ❌ **Transaction locking** (`TransactionsLocking`) — no period close; posted periods stay editable
- ❌ **Bank feeds** (`Plaid`/`BankingPlaid`) — import is manual CSV only
- ❌ **Bank rules engine** (`BankRules`, `BankingCategorize`, `BankingTranasctionsRegonize`) — the
  port has a hand-rolled `auto_match_transactions` in `financial.py`, but no user-definable rules
- ❌ **Landed costs** (`BillLandedCosts`)
- ❌ **Auto-increment document numbering** (`AutoIncrementOrders`)
- ❌ **Projects / cost centers** — no project tracking or profitability

## 3. Inventory & Warehouse

- ❌ Inventory adjustments (`InventoryAdjutments`) — no stock adjustment or cycle counting
- ❌ Multi-warehouse (`Warehouses`, `WarehousesTransfers`)
- ❌ Branches (`Branches`) — no multi-branch operations or branch-scoped reporting
- ❌ Bill of materials / assembly items
- ❌ All inventory reports (see §4)

## 4. Financial Reporting — 7 of 20 ported

| Report | Status |
|---|---|
| Balance Sheet | ✅ |
| Profit & Loss | ✅ |
| Trial Balance | ✅ |
| General Ledger | ✅ |
| Cash Flow | ✅ |
| Receivable (customer) Aging | ✅ |
| Payable (vendor) Aging | ⚠️ stub, no data |
| Sales Tax Liability Summary | ⚠️ partially covered by AU BAS |
| Journal Sheet | ❌ |
| Sales by Items | ❌ |
| Purchases by Items | ❌ |
| Inventory Valuation | ❌ *(linked from `reports/index.html` → 500)* |
| Inventory Item Details | ❌ |
| Customers Balance Summary | ❌ |
| Vendors Balance Summary | ❌ |
| Transactions by Customers | ❌ |
| Transactions by Vendors | ❌ |
| Realized Gain/Loss | ❌ *(blocked on multi-currency)* |
| Unrealized Gain/Loss | ❌ *(blocked on multi-currency)* |
| Project Profitability | ❌ *(blocked on Projects)* |

Additionally: `reports/aging.py` and `reports/inventory.py` are **0-byte files**. (`custom.py` and
`advanced.py` *are* registered — an earlier revision of this report claimed otherwise, having
misread a stale duplicate of `register_reports_blueprints()` that used to sit in `expenses.py`. That
dead copy has since been deleted.)

**Report output:** ❌ no PDF export anywhere —
[reports/financial.py:623](packages/webapp/src/routes/reports/financial.py#L623) returns the literal
string `"PDF export not implemented yet"`. `reportlab` and `WeasyPrint` are pinned in
`requirements-python.txt` but imported by zero files.

**Dashboard analytics:** ❌ no KPI widgets, interactive charts, budgeting or forecasting.

## 5. System Administration & Security

- ❌ **RBAC** — the original has `Roles`, `RolePermission`, `ViewRole` and `InviteUser` models. The
  port has a single `role = db.Column(db.String(50))` on `User`
  ([models/__init__.py:143](packages/server/src/models/__init__.py#L143)) and **no permission checks
  anywhere in the codebase**. Sidebar visibility is likewise unconditional.
- ❌ **User management** — no user list, no invite flow, no activity tracking
- ❌ **Audit trail** — no transaction audit log or data-change tracking
- ❌ **Attachments** (`Attachments` + `S3`) — no file attachments on any transaction
- ❌ **Saved/custom views** (`CustomViews`, `Views`, `DynamicListing`, `Resource`) — every list page
  is fixed-column with no user filtering or column customization
- ❌ **Universal search** (`Search`/`UniversalSearch`)
- ❌ **Document/PDF templates** (`PdfTemplate`, `TemplateInjectable`, `ChromiumlyTenancy`,
  `BrandingTemplates`)
- ⚠️ **CSRF is globally disabled** — `WTF_CSRF_ENABLED = False` in [app.py:52](app.py#L52), with the
  code's own comment saying it should be on for production. Every form POST is unprotected.
- ⚠️ **`SECRET_KEY` falls back to a hardcoded dev value** ([app.py:49](app.py#L49))

## 6. Integrations & Notifications

- ❌ **Email** (`Mail`, `MailNotification`, `MailTenancy`) — no `smtplib` or `Flask-Mail` usage
  anywhere, despite `Flask-Mail` being pinned. Blocks invoice delivery, password reset, and every
  notification.
- ❌ **Online payments** (`StripePayment`, `PaymentServices`, `PaymentLinks`)
- ❌ **Subscription/billing** (`Subscription`)
- ❌ Webhooks; QuickBooks import; e-commerce/CRM integrations
- ❌ OpenAPI/Swagger docs, API rate limiting

**API consistency issue:** 11 of 16 API blueprints use `@require_api_key`, but `bills.py`,
`expenses.py` and `sale_receipts.py` use `@login_required` instead — so those 10 endpoints are
unreachable to API-key clients. No API exists for estimates, credit notes or vendor credits.

## 7. Performance, Testing & Ops

- ❌ **No test suite for the Python app.** `test_mvp_api.py` is a live-server smoke script; the only
  real specs (`e2e/*.spec.ts`, `test/jest-e2e.json`) still target the React app.
- ❌ Background task processing (Celery), caching layer, structured logging/monitoring
- ⚠️ Repo hygiene: 14 committed `.bak` files across `routes/` and `routes/reports/`, plus four stray
  `.tsx` files in the Python routes directory. `user-management-code/` appears to be an unmerged
  scratch copy that nothing imports.

---

## Priority Recommendations

**Blocking — cleared 2026-08-02**
1. ~~Rebuild the virtualenv.~~ Done — rebuilt on Python 3.14 with bumped pins; app starts.
2. ~~Fix the broken `url_for` targets.~~ Done — 0 remain, verified against the live `url_map`.
   (There were 11, not 14; three were inside a Jinja comment and never rendered.)
3. ~~Relink the sidebar.~~ Done — four links repointed at the `financial.*` pages.

**High — core correctness**
4. ~~Rewrite `accounts.py` against the `Account` model.~~ Done — see the table above.
5. Clear the remaining 500s: the `'liabilitys'` KeyError and PostgreSQL-only `date_trunc` in
   `api/v1/reports.py`, and the missing `payments/edit.html`.
6. Enable CSRF and require a real `SECRET_KEY`.
7. Stand up a real test suite before the items below start changing accounting behaviour.
8. Email + PDF (dependencies already pinned) — unblocks registration, password reset and invoice delivery.
9. Fill in the aging/inventory/journal reports; give `aging.py` and `inventory.py` content.

**Medium**
10. RBAC with real permission checks, then user management and invites.
11. Inventory costing and inventory adjustments.
12. Multi-currency with an exchange-rate table.
13. Transaction locking / period close.
14. Broaden import/export beyond three resources; unify API auth.
15. An account-subtype column, to reach parity with the original's 19 fine-grained account types
    (the rewritten Chart of Accounts currently offers the five root types the schema can store).

**Lower** — bank feeds and rules, warehouses/branches, projects, attachments, saved views,
online payments, subscriptions, background processing.

---

## Conclusion

The port covers the **sales and purchase document lifecycle well** — invoices, estimates, receipts,
bills, credit notes, vendor credits, expenses and payments are all implemented with genuine
double-entry GL posting behind them. That is a real accounting core, and it is further along than the
previous revision of this report suggested for those modules.

As of the 2026-08-02 remediation pass the **Chart of Accounts is real** — it reads and writes the
`Account` table and derives balances from the ledger, so the screen and the books finally agree. The
small mechanical defects that were masking the true state of the port (broken route names, an
unlinked sidebar, a boot-blocking duplicate blueprint registration, a dead virtualenv) are cleared.

Two gaps remain, and they are the substantive ones: **reporting depth** is roughly a third of the
original, and every **platform concern** (RBAC, multi-currency, PDF, email, attachments, saved views,
inventory costing, period locking) is still absent. Neither is mechanical; both are real
implementation work.

The most valuable next step is not a feature. There is **no test suite for the Python app**, and
everything remaining on the roadmap changes accounting behaviour. That should come first.

The PRE-ALPHA warning in the README remains accurate; this is not yet safe for real financial data.

---
*Comparison base: BigCapital TypeScript/React version, in-repo*
