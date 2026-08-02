import os, sys, warnings, logging
SCRATCH=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.tmp')
os.makedirs(SCRATCH, exist_ok=True)
os.environ['DATABASE_URL']=f'sqlite:///{SCRATCH}/coa.db'
os.environ['SECRET_KEY']='t'
if os.path.exists(f'{SCRATCH}/coa.db'): os.remove(f'{SCRATCH}/coa.db')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore'); logging.disable(logging.CRITICAL)
import app as m
from decimal import Decimal
from datetime import date
from packages.server.src.database import db
from packages.server.src.models import (User, Organization, Account, AccountType,
                                        JournalEntry, JournalLineItem)
a=m.app; a.config['WTF_CSRF_ENABLED']=False
P=F=0
def check(label, cond, extra=''):
    global P,F
    if cond: P+=1; print(f'  PASS  {label}')
    else:    F+=1; print(f'  FAIL  {label} {extra}')

with a.app_context():
    db.create_all()
    org=Organization(name='T', email='t@t.local'); db.session.add(org); db.session.commit()
    u=User(email='t@t.local', first_name='T', last_name='T', organization_id=org.id, role='admin', is_active=True)
    u.set_password('x'); db.session.add(u); db.session.commit()
    ORG, UID = org.id, u.id

c=a.test_client()
with c.session_transaction() as s:
    s['_user_id']=str(UID); s['_fresh']=True

print('\n--- create ---')
r=c.post('/accounts/new', data={'code':'1000','name':'Cash at Bank','type':'asset',
    'parent_id':'0','description':'Main','opening_balance':'0','is_active':'y'}, follow_redirects=True)
check('POST /accounts/new returns 200', r.status_code==200, r.status_code)
with a.app_context():
    acc=Account.query.filter_by(code='1000').first()
    check('account persisted to DB', acc is not None)
    check('type stored as enum', acc and acc.type==AccountType.ASSET, acc.type if acc else None)
    CASH=acc.id

r=c.post('/accounts/new', data={'code':'4000','name':'Sales Revenue','type':'income',
    'parent_id':'0','opening_balance':'0','is_active':'y'}, follow_redirects=True)
with a.app_context():
    REV=Account.query.filter_by(code='4000').first().id

print('\n--- duplicate code rejected ---')
c.post('/accounts/new', data={'code':'1000','name':'Dupe','type':'asset','parent_id':'0',
    'opening_balance':'0','is_active':'y'}, follow_redirects=True)
with a.app_context():
    check('duplicate code not created', Account.query.filter_by(code='1000').count()==1,
          Account.query.filter_by(code='1000').count())

print('\n--- balances from journal lines ---')
with a.app_context():
    je=JournalEntry(entry_number='JE1', date=date.today(), description='sale',
                    debit_total=Decimal('100'), credit_total=Decimal('100'),
                    organization_id=ORG, created_by=UID, status='posted')
    db.session.add(je); db.session.flush()
    db.session.add(JournalLineItem(journal_entry_id=je.id, account_id=CASH, debit=Decimal('100'), credit=0))
    db.session.add(JournalLineItem(journal_entry_id=je.id, account_id=REV,  debit=0, credit=Decimal('100')))
    db.session.commit()

r=c.get('/accounts/')
body=r.get_data(as_text=True)
check('index 200', r.status_code==200, r.status_code)
check('asset debit balance shows +100', '100.00' in body)
from packages.webapp.src.routes.accounts import _journal_balances, _natural_balance
with a.app_context():
    nets=_journal_balances(ORG)
    cash=Account.query.get(CASH); rev=Account.query.get(REV)
    check('cash net = +100', nets[CASH]==Decimal('100'), nets.get(CASH))
    check('revenue net = -100', nets[REV]==Decimal('-100'), nets.get(REV))
    check('cash natural balance = +100 (debit-normal)', _natural_balance(cash, nets[CASH])==Decimal('100'))
    check('revenue natural balance = +100 (credit-normal)', _natural_balance(rev, nets[REV])==Decimal('100'))

print('\n--- edit ---')
r=c.post(f'/accounts/{CASH}/edit', data={'code':'1001','name':'Cash at Bank (renamed)',
    'type':'asset','parent_id':'0','opening_balance':'0','is_active':'y'}, follow_redirects=True)
check('edit 200', r.status_code==200, r.status_code)
with a.app_context():
    acc=Account.query.get(CASH)
    check('edit persisted code', acc.code=='1001', acc.code)
    check('edit persisted name', 'renamed' in acc.name, acc.name)

print('\n--- delete guards ---')
r=c.post(f'/accounts/{CASH}/delete', follow_redirects=True)
with a.app_context():
    check('delete blocked: account has journal lines', Account.query.get(CASH) is not None)

with a.app_context():
    child=Account(code='1002', name='Petty Cash', type=AccountType.ASSET, parent_id=CASH,
                  organization_id=ORG, is_active=True, opening_balance=0, current_balance=0)
    db.session.add(child); db.session.commit(); CHILD=child.id
    parent=Account(code='2000', name='Payables', type=AccountType.LIABILITY, organization_id=ORG,
                   is_active=True, opening_balance=0, current_balance=0)
    db.session.add(parent); db.session.commit(); PAY=parent.id
    kid=Account(code='2001', name='Trade Payables', type=AccountType.LIABILITY, parent_id=PAY,
                organization_id=ORG, is_active=True, opening_balance=0, current_balance=0)
    db.session.add(kid); db.session.commit(); KID=kid.id

r=c.post(f'/accounts/{PAY}/delete', follow_redirects=True)
with a.app_context():
    check('delete blocked: account has children', Account.query.get(PAY) is not None)

r=c.post(f'/accounts/{KID}/delete', follow_redirects=True)
with a.app_context():
    check('delete allowed: leaf with no journal lines', Account.query.get(KID) is None)

print('\n--- cycle prevention ---')
from packages.webapp.src.routes.accounts import _parent_choices, _descendant_ids
with a.app_context():
    check('descendants of CASH include CHILD', CHILD in _descendant_ids(CASH, ORG))
    ids=[i for i,_ in _parent_choices(ORG, exclude_id=CASH)]
    check('own descendant excluded from parent choices', CHILD not in ids)
    check('self excluded from parent choices', CASH not in ids)

print('\n--- show / tenancy ---')
check('show 200', c.get(f'/accounts/{CASH}').status_code==200)
check('unknown account redirects', c.get('/accounts/99999').status_code==302)
with a.app_context():
    other=Organization(name='O2', email='o2@t.local'); db.session.add(other); db.session.commit()
    foreign=Account(code='9999', name='Foreign', type=AccountType.ASSET, organization_id=other.id,
                    is_active=True, opening_balance=0, current_balance=0)
    db.session.add(foreign); db.session.commit(); FID=foreign.id
check('other org account not visible', c.get(f'/accounts/{FID}').status_code==302)
r=c.get('/accounts/')
check('other org account absent from index', 'Foreign' not in r.get_data(as_text=True))

print('\n--- filters ---')
check('type filter 200', c.get('/accounts/?type=asset').status_code==200)
check('bad type filter does not 500', c.get('/accounts/?type=nonsense').status_code==200)
check('search filter 200', c.get('/accounts/?search=Cash').status_code==200)
check('status filter 200', c.get('/accounts/?status=inactive').status_code==200)

print(f'\n=== {P} passed, {F} failed ===')
sys.exit(1 if F else 0)
