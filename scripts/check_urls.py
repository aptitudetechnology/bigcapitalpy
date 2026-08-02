import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as appmod
a = appmod.app
valid = {r.endpoint for r in a.url_map.iter_rules()}
tdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'packages/webapp/src/templates')
JINJA_COMMENT = re.compile(r'\{#.*?#\}', re.S)
HTML_COMMENT  = re.compile(r'<!--.*?-->', re.S)
used, commented = {}, {}
for dp, _, fns in os.walk(tdir):
    for fn in fns:
        if not fn.endswith('.html'): continue
        p = os.path.join(dp, fn); rel = os.path.relpath(p, tdir)
        raw = open(p, encoding='utf-8', errors='replace').read()
        live = HTML_COMMENT.sub('', JINJA_COMMENT.sub('', raw))
        live_eps = set(re.findall(r"url_for\(\s*['\"]([^'\"]+)['\"]", live))
        all_eps  = set(re.findall(r"url_for\(\s*['\"]([^'\"]+)['\"]", raw))
        for e in live_eps: used.setdefault(e, set()).add(rel)
        for e in all_eps - live_eps: commented.setdefault(e, set()).add(rel)
missing = {e: f for e, f in used.items() if e not in valid}
dead = {e: f for e, f in commented.items() if e not in valid and e not in used}
print(f"registered endpoints: {len(valid)}   live url_for targets: {len(used)}")
print(f"\n=== BROKEN, RENDERED ({len(missing)}) ===")
for e in sorted(missing):
    print(f"  {e:42s} <- {', '.join(sorted(missing[e]))}")
print(f"\n=== broken but inside comments, harmless ({len(dead)}) ===")
for e in sorted(dead):
    print(f"  {e:42s} <- {', '.join(sorted(dead[e]))}")
