import io,sys,glob,os,hashlib,shutil
R=lambda p:io.open(p,encoding='utf-8').read()
H=lambda p:hashlib.sha256(io.open(p,'rb').read()).hexdigest()
E,Q='references/execution.md','references/quality-gates.md'
def desc(p):
 for ln in R(p).splitlines():
  if ln.startswith('description:'):return ln[12:].strip()
 return ''
if sys.argv[1:]==['init']:
 os.makedirs('_baseline',exist_ok=True)
 for f in[E,Q]:shutil.copy2(f,'_baseline/'+os.path.basename(f))
 fs=set()
 for g in['scripts/*.py','companion-skills/*/agents/*.yaml','assets/**/*.*','references/*.md']:
  fs|={p.replace(os.sep,'/')for p in glob.glob(g,recursive=True)if os.path.isfile(p)}
 io.open('_baseline/readonly-sha.txt','w',encoding='utf-8').write('\n'.join(H(p)+' '+p for p in sorted(fs)if p not in{E,Q}))
 print('init ok');sys.exit(0)
bad=[]
def cap(n,v,lim):
 print(n,v,'/',lim,'OK' if v<=lim else'FAIL')
 if v>lim:bad.append(n)
cap('desc主',len(desc('SKILL.md')),130)
cap('desc策略',len(desc('companion-skills/wechat-content-strategy/SKILL.md')),160)
cap('desc学习',len(desc('companion-skills/wechat-style-learning/SKILL.md')),160)
cap('SKILL.md',len(R('SKILL.md')),1750)
ex=sorted(glob.glob('references/execution*.md')+glob.glob('references/execution/*.md'))
qg=sorted(glob.glob('references/quality-gates*.md')+glob.glob('references/quality-gates/*.md'))
for f in ex+qg:cap(f,len(R(f)),4500)
cap('execution总和',sum(len(R(f))for f in ex),14546)
cap('quality-gates总和',sum(len(R(f))for f in qg),10283)
body=R('SKILL.md')
bad+=['路由:'+f for f in ex+qg if f.replace('\\','/')not in body]
base={l for p in['_baseline/execution.md','_baseline/quality-gates.md']for l in R(p).splitlines()if l.strip()}
new={l for f in ex+qg for l in R(f).splitlines()if l.strip()}
mis=base-new
if mis:bad.append('丢行');print('丢行:',len(mis),[m[:50]for m in sorted(mis)[:5]])
ro=[p for ln in R('_baseline/readonly-sha.txt').splitlines()for h,p in[ln.split(' ',1)]if not os.path.exists(p)or H(p)!=h]
if ro:bad.append('只读');print('只读改动:',len(ro),ro[:5])
for a in['cheat-init','references/onboarding.md','references/publishing.md']:
 if a not in body:bad.append('锚点:'+a)
print('RESULT:','PASS' if not bad else'FAIL '+','.join(bad))
