import ast, os
ROOT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'packages/webapp/src')
TPL=os.path.join(ROOT,'templates')
missing=[]
for dp,_,fns in os.walk(ROOT):
    if '__pycache__' in dp: continue
    for fn in fns:
        if not fn.endswith('.py'): continue
        p=os.path.join(dp,fn)
        try: tree=ast.parse(open(p).read())
        except Exception: continue
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):
                f=n.func
                name=getattr(f,'id',None) or getattr(f,'attr',None)
                if name=='render_template' and n.args and isinstance(n.args[0],ast.Constant):
                    t=n.args[0].value
                    if isinstance(t,str) and not os.path.isfile(os.path.join(TPL,t)):
                        missing.append((os.path.relpath(p,ROOT), n.lineno, t))
print(f"=== render_template targets that DO NOT EXIST ({len(missing)}) ===")
for f,l,t in sorted(missing):
    print(f"  {f}:{l}  ->  {t}")
