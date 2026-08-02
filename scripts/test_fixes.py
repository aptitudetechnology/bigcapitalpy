"""Regression tests for three defects fixed on 2026-08-02.

1. api/v1/reports.py balance_sheet_report raised KeyError 'liabilitys'
   (naive pluralisation of the AccountType value).
2. api/v1/reports.py dashboard_metrics used PostgreSQL-only date_trunc(),
   which raised "no such function" on SQLite.
3. routes/payments.py edit() rendered payments/edit.html, which did not exist,
   and was GET-only so had no way to save.
"""
import os, sys, json, warnings, logging
SCRATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.tmp')
os.makedirs(SCRATCH, exist_ok=True)
os.environ['DATABASE_URL'] = f'sqlite:///{SCRATCH}/fixes.db'
os.environ['SECRET_KEY'] = 't'
if os.path.exists(f'{SCRATCH}/fixes.db'):
    os.remove(f'{SCRATCH}/fixes.db')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore'); logging.disable(logging.CRITICAL)
import app as m
from decimal import Decimal
from datetime import date, timedelta
from packages.server.src.database import db
from packages.server.src.models import (User, Organization, Account, AccountType, Customer,
                                        Invoice, InvoiceStatus, Payment, PaymentMethod)

a = m.app; a.config['WTF_CSRF_ENABLED'] = False
P = F = 0
def check(label, cond, extra=''):
    global P, F
    if cond: P += 1; print(f'  PASS  {label}')
    else:    F += 1; print(f'  FAIL  {label} {extra}')

with a.app_context():
    db.create_all()
    org = Organization(name='T', email='t@t.local'); db.session.add(org); db.session.commit()
    u = User(email='t@t.local', first_name='T', last_name='T', organization_id=org.id,
             role='admin', is_active=True)
    u.set_password('x'); db.session.add(u); db.session.commit()
    ORG, UID = org.id, u.id

    accs = {}
    for code, name, t in [('1000', 'Bank', AccountType.ASSET), ('2000', 'Payables', AccountType.LIABILITY),
                          ('3000', 'Capital', AccountType.EQUITY), ('4000', 'Sales', AccountType.INCOME),
                          ('5000', 'Rent', AccountType.EXPENSE)]:
        acc = Account(code=code, name=name, type=t, organization_id=ORG, is_active=True,
                      opening_balance=0, current_balance=0)
        db.session.add(acc); db.session.commit(); accs[name] = acc.id

    cust = Customer(display_name='Acme', organization_id=ORG, is_active=True)
    db.session.add(cust); db.session.commit(); CUST = cust.id

    today = date.today()
    # Two invoices in different months, to exercise the month grouping.
    for n, offset in [('INV-1', 10), ('INV-2', 45)]:
        d = today - timedelta(days=offset)
        db.session.add(Invoice(invoice_number=n, invoice_date=d, due_date=d + timedelta(days=30),
                               customer_id=CUST, subtotal=Decimal('100'), total=Decimal('100'),
                               balance=Decimal('100'), status=InvoiceStatus.SENT, organization_id=ORG))
    db.session.commit()

    pay = Payment(payment_number='PAY-1', payment_date=today, amount=Decimal('50'),
                  payment_method=PaymentMethod.CASH, customer_id=CUST,
                  deposit_account_id=accs['Bank'], organization_id=ORG, created_by=UID,
                  reference='orig-ref', notes='orig-notes')
    db.session.add(pay); db.session.commit(); PAY = pay.id

c = a.test_client()
with c.session_transaction() as s:
    s['_user_id'] = str(UID); s['_fresh'] = True

print('\n--- fix 1: balance sheet KeyError ---')
r = c.get('/api/v1/reports/balance-sheet')
check('GET /api/v1/reports/balance-sheet is 200', r.status_code == 200, r.status_code)
if r.status_code == 200:
    rep = json.loads(r.get_data(as_text=True))['data']['report']
    check('has assets section', 'assets' in rep)
    check('has liabilities section (was "liabilitys")', 'liabilities' in rep)
    check('has equity section', 'equity' in rep)
    check('no misspelled key present', 'liabilitys' not in rep)

print('\n--- fix 2: dashboard metrics date_trunc ---')
r = c.get('/api/v1/reports/dashboard-metrics')
check('GET /api/v1/reports/dashboard-metrics is 200', r.status_code == 200, r.status_code)
if r.status_code == 200:
    met = json.loads(r.get_data(as_text=True))['data']['metrics']
    trends = met['monthly_trends']
    check('monthly_trends populated', len(trends) == 2, trends)
    check('month formatted YYYY-MM', all(len(t['month']) == 7 and t['month'][4] == '-' for t in trends), trends)
    check('trends sorted chronologically', [t['month'] for t in trends] == sorted(t['month'] for t in trends), trends)

print('\n--- fix 3: payment edit ---')
r = c.get(f'/payments/{PAY}/edit')
check('GET /payments/<id>/edit is 200', r.status_code == 200, r.status_code)
body = r.get_data(as_text=True)
check('form shows existing reference', 'orig-ref' in body)
check('locked amount shown for context', '50.00' in body)

r = c.post(f'/payments/{PAY}/edit', data={
    'payment_method': 'bank_transfer', 'reference': 'new-ref',
    'notes': 'new-notes', 'bank_name': 'Big Bank', 'check_number': '123',
}, follow_redirects=True)
check('POST /payments/<id>/edit is 200', r.status_code == 200, r.status_code)
with a.app_context():
    p = Payment.query.get(PAY)
    check('reference saved', p.reference == 'new-ref', p.reference)
    check('notes saved', p.notes == 'new-notes', p.notes)
    check('bank_name saved', p.bank_name == 'Big Bank', p.bank_name)
    check('check_number saved', p.check_number == '123', p.check_number)
    check('payment_method saved', p.payment_method == PaymentMethod.BANK_TRANSFER, p.payment_method)
    check('amount untouched (ledger safe)', p.amount == Decimal('50.00'), p.amount)
    check('payment_date untouched (ledger safe)', p.payment_date == today, p.payment_date)
    check('deposit account untouched (ledger safe)', p.deposit_account_id == accs['Bank'])
    check('customer untouched (ledger safe)', p.customer_id == CUST)

r = c.post(f'/payments/{PAY}/edit', data={'payment_method': 'not_a_method'}, follow_redirects=True)
check('invalid payment method rejected, no 500', r.status_code == 200, r.status_code)
with a.app_context():
    check('invalid method did not persist',
          Payment.query.get(PAY).payment_method == PaymentMethod.BANK_TRANSFER)

print(f'\n=== {P} passed, {F} failed ===')
sys.exit(1 if F else 0)
