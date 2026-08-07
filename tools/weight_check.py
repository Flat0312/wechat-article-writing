import io,glob,sys
R=lambda p:io.open(p,encoding='utf-8').read()
bad=[]
def need(n,t,s):
 if s not in t:bad.append(n+' 缺:'+s)
def ban(n,t,s):
 if s in t:bad.append(n+' 残留:'+s)
style=R('references/writing-style.md')
routing=R('references/skill-routing.md')
readme=R('README.md')
exe=''.join(R(f) for f in glob.glob('references/execution*.md')+glob.glob('references/execution/*.md'))
comp=R('companion-skills/wechat-content-strategy/SKILL.md')
need('style',style,'每篇中长文必需的主要写作增强')
need('style',style,'不创建作者画像')
need('style',style,'observe-final')
need('routing',routing,'必需的活人感正文主流程')
need('SKILL',R('SKILL.md'),'observe-final')
for n,t in [('style',style),('routing',routing),('readme',readme),('execution',exe),('strategy',comp)]:
 need(n,t,'同权重')
need('style',style,'只凭转述不算调用')
ban('style',style,'5. `human-writing`')
ban('readme',readme,'主导')
print('RESULT:','PASS' if not bad else'FAIL')
for b in bad:print(' ',b)
sys.exit(1 if bad else 0)