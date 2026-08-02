import os, sys, warnings
SCRATCH=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.tmp')
os.makedirs(SCRATCH, exist_ok=True)
os.environ['DATABASE_URL']=f'sqlite:///{SCRATCH}/smoke.db'
os.environ['SECRET_KEY']='smoke-test-key'
if os.path.exists(f'{SCRATCH}/smoke.db'): os.remove(f'{SCRATCH}/smoke.db')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')
import logging
logging.disable(logging.CRITICAL)
import app as m
from packages.server.src.database import db
from packages.server.src.models import User, Organization

a = m.app
a.config['WTF_CSRF_ENABLED']=False
with a.app_context():
    db.create_all()
    org = Organization(name='Smoke Co', email='smoke@test.local')
    db.session.add(org); db.session.commit()
    u = User(email='smoke@test.local', first_name='S', last_name='T',
             organization_id=org.id, role='admin', is_active=True)
    u.set_password('smokepass123')
    db.session.add(u); db.session.commit()

c = a.test_client()
with c.session_transaction() as s:
    s['_user_id'] = '1'
    s['_fresh'] = True

rules = [r for r in a.url_map.iter_rules()
         if 'GET' in r.methods and not r.arguments and r.endpoint != 'static']
results=[]
for r in sorted(rules, key=lambda r: str(r.rule)):
    try:
        resp = c.get(str(r.rule), follow_redirects=False)
        results.append((resp.status_code, str(r.rule), r.endpoint, ''))
    except Exception as e:
        results.append((599, str(r.rule), r.endpoint, f'{type(e).__name__}: {e}'))

bad=[x for x in results if x[0]>=500]
ok=[x for x in results if x[0]<400]
red=[x for x in results if 300<=x[0]<400]
print(f"GET-able no-arg routes: {len(results)}   2xx:{len(ok)}  3xx:{len(red)}  >=500:{len(bad)}")
print("\n=== FAILING (>=500) ===")
for code,rule,ep,err in bad:
    print(f"  {code}  {rule:45s} {ep}")
    if err: print(f"        {err[:300]}")
