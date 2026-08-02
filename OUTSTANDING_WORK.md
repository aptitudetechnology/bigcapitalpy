# BigCapitalPy — Outstanding Work vs. the React/NestJS Original

Audit date: 2026-08-02 · Branch: `development` @ `da35365ca`
**Updated 2026-08-02 after a first remediation pass — see [Progress](#progress).**

## Progress

Done in the first pass (all verified against a running app):

- ✅ **Virtualenv rebuilt on Python 3.14**, pins bumped. The app starts; 253 routes register.
- ✅ **All broken `url_for` targets fixed** — 0 remain (verified against the live `url_map`).
- ✅ **Sidebar relinked** to `financial.*` pages that already existed.
- ✅ **Two report pages fixed** that were raising `TemplateNotFound`.
- ✅ **Chart of Accounts rewritten** against the `Account` model — real CRUD, balances
  derived from journal lines, parent/child tree, delete guards, org scoping. 27/27 functional
  tests pass.

Two corrections to the original audit, found while fixing:

1. **"14 broken `url_for` targets" was 11.** The three inventory-report links in
   `reports/index.html` sit inside a `{# … #}` Jinja comment and never render. My original scanner
   was a regex that did not strip Jinja comments.
2. **"`custom.py`/`advanced.py` are never registered" was wrong.** Both *are* registered by
   `reports/__init__.py`. I had read a **stale duplicate** of `register_reports_blueprints()` that
   was sitting unused at the bottom of `reports/expenses.py`. That dead copy has been deleted.

Still open — see [§1](#1-still-open) and the [work order](#suggested-order-of-work).

Both codebases live in this repo, which makes a direct comparison possible:

- **Original (TypeScript):** `packages/server/src/modules/**` (NestJS, 76 modules) and
  `packages/webapp/src/containers/**` + `packages/webapp/src/routes/dashboard.tsx` (React, ~95 routes).
- **Port (Python):** `packages/server/src/models/__init__.py` (SQLAlchemy),
  `packages/webapp/src/routes/*.py` (Flask blueprints), `packages/webapp/src/api/v1/*.py`,
  `packages/webapp/src/templates/**` (111 Jinja templates).

Roughly **70 Python files + 111 templates** stand against **4,874 TS/TSX files**. The port covers the
core sales/purchase document lifecycle well; the gaps are concentrated in the chart of accounts,
inventory, reporting depth, and every "platform" concern (RBAC, multi-currency, PDF, email).

---

## 1. Still open

Defects found during the remediation pass that were **not** in the agreed scope, so they remain:

| Issue | Location | Effect |
|---|---|---|
| `KeyError: 'liabilitys'` | [api/v1/reports.py:201](packages/webapp/src/api/v1/reports.py#L201) | `GET /api/v1/reports/balance-sheet` → 500. Naive `+ 's'` pluralisation of the section name. |
| `date_trunc` is PostgreSQL-only | [api/v1/reports.py:439](packages/webapp/src/api/v1/reports.py#L439) | `GET /api/v1/reports/dashboard-metrics` → 500 on SQLite, which is the default dev database. |
| `payments/edit.html` does not exist | [routes/payments.py:339](packages/webapp/src/routes/payments.py#L339) | Editing a payment → `TemplateNotFound` 500. |
| `create_app()` is not idempotent | [routes/reports/__init__.py:5](packages/webapp/src/routes/reports/__init__.py#L5) | `reports_bp` is a module-level singleton that accumulates sub-blueprint registrations, so a second `create_app()` raises. Blocks any test suite that builds more than one app instance. |
| Conflicting SQLAlchemy relationships | [models/__init__.py](packages/server/src/models/__init__.py) | `BankTransaction.bank_account` and `BankTransaction.account` both write `bank_transactions.account_id`; emits `SAWarning` on every boot and can silently clobber. |
| `instance/bigcapitalpy.db` is stale | — | Predates the `users.api_key` column; any query on `User` fails with `no such column`. `add_api_key_migration.sql` at the repo root was never applied. |
| Dead root route | [app.py:164](app.py#L164) | `@app.route('/')` renders `dashboard.html`, which does not exist. Harmless only because `dashboard_bp` registers `/` first and wins. |

### Fixed in this pass

- All 11 genuinely-broken `url_for` targets (endpoint renames, nested-blueprint names, and the
  missing `accounts.edit` / `accounts.delete` routes).
- `estimates_bp` was registered twice — once inside `register_blueprints()` and again in
  [app.py](app.py) — which raised `ValueError` on boot under Flask 3. The blueprint already declares
  its own `url_prefix`, so the duplicate was removed.
- A stale, unused duplicate of `register_reports_blueprints()` at the bottom of
  `reports/expenses.py` (deleted — it is what caused correction #2 above).
- `reports.advanced.profitability_analysis` pointed at a non-existent template; now points at the
  existing `reports/profitability.html`. `reports.advanced.executive_dashboard` had no template at
  all; given the route serves nothing but hardcoded zeros, it now renders an honest placeholder in
  the same style as the neighbouring one rather than 500-ing.

**Virtualenv:** rebuilt on Python 3.14. `requirements-python.txt` pins were bumped (Flask 2.3→3.1,
Werkzeug 2.3→3.1, numpy 1.26→2.5, pandas 2.1→3.0, SQLAlchemy 2.0.21→2.0.51 and others); the
`configparser` and `pycycle` pins were dropped. Verified to install cleanly into a fresh venv.

---

## 2. Stubs that look implemented but aren't

### ~~Chart of Accounts is entirely mock data~~ — fixed

Previously `accounts.py` never touched the database: `index()` rendered a hardcoded `SEED_ACCOUNTS`
list with every balance at `0.00`, `new()` discarded submitted input, and `show()` returned one of
two hardcoded fakes.

[accounts.py](packages/webapp/src/routes/accounts.py) has been rewritten against the `Account`
model:

- Real CRUD — `index`, `new`, `show`, plus the previously missing `edit` and `delete`.
- **Balances derived from `JournalLineItem`**, not from `Account.current_balance`. That column is
  only written by the manual-journal and bank-reconciliation flows in `financial.py`; invoices,
  bills, payments and expenses post journal entries without touching it, so it under-reports. The
  aggregation mirrors `reports/financial.py:trial_balance`, so the two views agree.
- Balances are sign-normalised by account type, so a credit-normal account (liability, equity,
  income) reads positive when it is in its natural direction.
- Parent/child tree, with cycle prevention — an account cannot be re-parented beneath its own
  descendant.
- Delete guards: refuses if the account has children, or if any journal line references it
  (directing the user to deactivate instead, preserving the audit trail).
- Every query is scoped to `current_user.organization_id`.
- One grouped balance query for the whole page rather than one per account.

Verified by 27 functional assertions covering persistence, duplicate-code rejection, balance signs
for both debit- and credit-normal accounts, edit round-trips, both delete guards, cycle prevention,
cross-organisation isolation, and filter handling.

**Known limitation:** `Account.type` is a five-value enum (asset/liability/equity/income/expense),
so the account-type picker offers those five. The original's 19 fine-grained types (bank,
accounts-receivable, …) in `accounts_constants.ACCOUNT_TYPES` have no column to live in; adding an
account-subtype column is follow-up work. `opening_balance` is stored but, consistent with the
existing Trial Balance report, is not currently folded into computed balances anywhere.

### Other no-op handlers

- **Registration** ([auth.py:41](packages/webapp/src/routes/auth.py#L41)) — POST flashes
  "Registration feature coming soon. Please use the demo account." There is no signup path at all.
  The React version has a full onboarding wizard (`containers/Setup`, `containers/OneClickDemo`).
- **User settings** ([users.py](packages/webapp/src/routes/users.py)) — `edit_settings()` and
  `settings()` flash success and save nothing. `profile()` still contains six `print()` debug
  statements that fire on every request.
- **Password reset** ([auth_api.py:174](packages/webapp/src/routes/auth_api.py#L174)) — returns
  success without sending mail; token validation is likewise unimplemented.
- **Organization settings/backup** ([organization.py:116](packages/webapp/src/routes/organization.py#L116))
  — both documented in-code as placeholders.
- **PDF export of reports** ([reports/financial.py:623](packages/webapp/src/routes/reports/financial.py#L623))
  — literally `return "PDF export not implemented yet"`.
- **Emailing invoices** ([invoices.py:391](packages/webapp/src/routes/invoices.py#L391)) — `# TODO: Send email to customer`.
- **Expense/purchase/vendor-aging reports** ([reports/expenses.py](packages/webapp/src/routes/reports/expenses.py))
  — all three render a template with no data; marked `# TODO: Replace with real data`.
- **Custom report builder** ([reports/custom.py](packages/webapp/src/routes/reports/custom.py)) — same.

### Report modules — corrected

`register_reports_blueprints()` in [reports/__init__.py](packages/webapp/src/routes/reports/__init__.py)
registers `tax`, `sales`, `financial`, `expenses`, `custom` **and** `advanced`. An earlier draft of
this report said `custom` and `advanced` were orphaned; that was a misreading of the stale duplicate
in `expenses.py` (now deleted).

Genuinely absent: `aging.py` and `inventory.py` are **0-byte files**, and `dashboard.py` defines
`reports_dashboard_bp`, which is deliberately not registered (`# reports_dashboard_bp import and
registration removed`) — `/reports` is served by `reports_bp.index` instead.

### ~~Sidebar routes everything to one page~~ — fixed

[base.html](packages/webapp/src/templates/base.html) now links Financial Dashboard, Manual Journals,
Bank Reconciliation and Cash Flow to `financial.index`, `financial.manual_journals`,
`financial.reconciliation` and `financial.cash_flow`. (Banking was already correctly linked, so it
was four links, not five.)

---

## 3. NestJS modules with no Python counterpart

Grouped by how much they would matter to a user of the Python app.

**Accounting correctness**
- `InventoryCost` — no FIFO/average costing engine. Items have no cost layers, so COGS is not computed.
- `InventoryAdjutments` — no stock adjustment workflow.
- `Currencies` — `currency` is a bare `String(3)` column on 11 models with **no exchange-rate table
  and no revaluation**. Multi-currency is nominal only; `RealizedGainLoss` / `UnrealizedGainLoss`
  reports are consequently impossible.
- `TransactionsLocking` — no period close / lock date, so posted periods can be edited freely.
- `BillLandedCosts` — not ported.
- `AutoIncrementOrders` — no configurable document numbering.

**Platform / access control**
- `Roles`, `RolePermission`, `ViewRole` — the Python `User` model has a single
  `role = db.Column(db.String(50))` string ([models/__init__.py:143](packages/server/src/models/__init__.py#L143))
  with no permission checks anywhere. No user list, no invite flow (`InviteUser.model.ts` unported).
- `Tenancy` / `TenantDBManager` — the original gives each tenant its own database; the port uses a
  single DB with an `organization_id` column. Defensible as a simplification, but organisation
  scoping is applied ad-hoc per query rather than enforced centrally.
- `Attachments` + `S3` — no file attachments on any transaction.
- `Search` / `UniversalSearch` — no global search.
- `CustomViews` / `Views` / `DynamicListing` / `Resource` — no saved views, custom columns, or
  reusable filtering. All Python list pages are fixed-column.
- `Branches`, `Warehouses`, `WarehousesTransfers` — no multi-location support.

**Integrations & output**
- `PdfTemplate`, `TemplateInjectable`, `ChromiumlyTenancy`, `BrandingTemplates` — **no PDF generation
  anywhere**. `reportlab` and `WeasyPrint` are pinned in `requirements-python.txt` but imported by
  zero files.
- `Mail`, `MailNotification`, `MailTenancy` — **no email**. `Flask-Mail` is likewise declared but
  never imported; no `smtplib` usage exists.
- `Plaid` / `BankingPlaid` — no automated bank feeds. Bank import is manual CSV
  (`import_bank_transactions.py`, `transform_airwallex_csv.py`).
- `BankRules`, `BankingCategorize`, `BankingTranasctionsRegonize`, `BankingTransactionsExclude` — the
  Python reconciliation in `financial.py` has a hand-rolled `auto_match_transactions`, but no
  user-definable rules engine.
- `StripePayment`, `PaymentServices`, `PaymentLinks` — no online payment collection.
- `Subscription` — no billing/plan management.
- `Projects` (React `containers/Projects`) — not ported.

**Lower impact:** `EventsTracker`, `Loops`, `Metable`, `Features`, `Miscellaneous`, `System`.

---

## 4. Financial reports: 7 of 20 ported

React defines 20 report routes under `/financial-reports/`. Python status:

| Report | Status |
|---|---|
| Balance Sheet | ✅ `reports/financial.py:428` |
| Profit & Loss | ✅ `:480` |
| Trial Balance | ✅ `:20` |
| General Ledger | ✅ `:102` |
| Cash Flow | ✅ `:226` |
| Receivable Aging (customer) | ✅ `reports/sales.py:43` |
| Payable Aging (vendor) | ⚠️ stub — template only, no data |
| Journal Sheet | ❌ |
| Sales by Items | ❌ |
| Purchases by Items | ❌ |
| Inventory Valuation | ❌ (linked from `reports/index.html` → 500) |
| Inventory Item Details | ❌ |
| Customers Balance Summary | ❌ |
| Vendors Balance Summary | ❌ |
| Transactions by Customers | ❌ |
| Transactions by Vendors | ❌ |
| Realized Gain/Loss | ❌ (blocked on multi-currency) |
| Unrealized Gain/Loss | ❌ (blocked on multi-currency) |
| Project Profitability | ❌ (blocked on Projects module) |
| Sales Tax Liability Summary | ⚠️ partially covered by the Australian GST/BAS report, `reports/tax.py:396` |

The port adds AU-specific reporting the original lacks (BAS, GST tax codes, `BASReport` model) — worth
keeping as a deliberate divergence rather than treating as drift.

---

## 5. REST API

84 endpoints across 16 blueprints in `packages/webapp/src/api/v1/`. Two consistency issues:

- **Mixed auth schemes.** 11 files use `@require_api_key`; `bills.py` (4 routes), `expenses.py` (3)
  and `sale_receipts.py` (3) use `@login_required` instead, so they are unreachable to API-key
  clients and only work from a browser session.
- **Coverage gaps** vs the web UI: no API for estimates, credit notes, vendor credits, manual
  journals beyond `journal.py`, or import/export.

Import/export ([import_export.py](packages/webapp/src/routes/import_export.py)) covers only
customers, vendors and items — 3 resources against ~15 importable resources in the React app.

---

## 6. Security and hygiene

- **CSRF is globally disabled** — `app.config['WTF_CSRF_ENABLED'] = False` in
  [app.py:52](app.py#L52), with the code's own comment noting it should be on for production. Every
  `FlaskForm` POST is unprotected.
- **`SECRET_KEY` defaults to `'dev-secret-key-change-in-production'`** ([app.py:49](app.py#L49)).
- **No test suite for the Python app.** `test_mvp_api.py` is a live-server smoke script; the only
  real specs (`e2e/*.spec.ts`, `test/jest-e2e.json`) target the React app. `user-management-code/`
  looks like an unmerged scratch copy — it contains `test_user.py`, `routes.py`, `user.py` and
  `forms.py` that nothing imports.
- **Backup files committed:** 6 × `backup.py.bak*`, 3 × `reports/__init__.py.bak*`,
  4 × `reports/financial.py.bak*`, plus `reports.py.bak`, `sales.py.bak`, `app.py.bak`. Also stray
  `.tsx` files still sitting in the Python routes directory (`dashboard.tsx`, `preferences.tsx`,
  `authentication.tsx`, `preferencesTabs.tsx`).

---

## Suggested order of work

~~1. Rebuild the venv so the app runs at all.~~ **done**
~~2. Fix the broken `url_for` targets.~~ **done**
~~3. Relink the sidebar to the financial pages that already exist.~~ **done**
~~4. Rewrite `accounts.py` against the `Account` model.~~ **done**

Next:

5. Clear the remaining §1 defects — they are all small: the `'liabilitys'` KeyError, the
   PostgreSQL-only `date_trunc`, the missing `payments/edit.html`, and the non-idempotent
   `create_app()`.
6. Apply `add_api_key_migration.sql` to `instance/bigcapitalpy.db`, or regenerate it, so the
   checked-in database matches the models.
7. Resolve the overlapping `BankTransaction` relationships before they corrupt bank data.
8. Enable CSRF; require a real `SECRET_KEY`.
9. Stand up a real test suite. There is currently none for the Python app — the Chart of Accounts
   work above was verified with a throwaway harness that should be made permanent, since every
   later item on this list changes accounting behaviour.
10. Implement registration + password reset (needs email, so pair with #11).
11. Add PDF and email — the dependencies are already pinned; invoices/estimates are unusable
    without them.
12. Fill in the aging, inventory and journal reports; give `aging.py` and `inventory.py` content.
13. Add RBAC (roles + permission checks), then user management/invites.
14. Longer term: an account-subtype column to reach parity with the original's 19 account types,
    inventory costing, multi-currency with exchange rates, transaction locking.
