"""Add three standard PowerPoint click-to-appear effects to the attack example."""
import sys,zipfile
from pathlib import Path
from lxml import etree as E
p=Path(sys.argv[1]);ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
def el(tag,**attrs):return E.Element('{'+ns['p']+'}'+tag,**{k:str(v) for k,v in attrs.items()})
with zipfile.ZipFile(p) as z:data={n:z.read(n) for n in z.namelist()}
r=E.fromstring(data['ppt/slides/slide2.xml']);ids=[]
for needle in ['Ignore the question.','② Model','③ Output']:
    matches=[s for s in r.findall('.//p:sp',ns) if needle in ''.join(s.xpath('.//a:t/text()',namespaces=ns))]
    assert len(matches)==1,(needle,len(matches))
    ids.append(matches[0].find('.//p:cNvPr',ns).get('id'))
t=el('timing');tl=el('tnLst');t.append(tl);par=el('par');tl.append(par);root=el('cTn',id=1,dur='indefinite',restart='never',nodeType='tmRoot');par.append(root);children=el('childTnLst');root.append(children);seq=el('seq',concurrent=1,nextAc='seek');children.append(seq);main=el('cTn',id=2,dur='indefinite',nodeType='mainSeq');seq.append(main);effects=el('childTnLst');main.append(effects)
for i,spid in enumerate(ids):
    base=3+i*4;outer=el('par');effects.append(outer);ct=el('cTn',id=base,fill='hold');outer.append(ct);conds=el('stCondLst');conds.append(el('cond',delay='indefinite'));ct.append(conds);chl=el('childTnLst');ct.append(chl)
    inner=el('par');chl.append(inner);effect=el('cTn',id=base+1,presetID=1,presetClass='entr',presetSubtype=0,fill='hold',grpId=0,nodeType='clickEffect');inner.append(effect);sc=el('stCondLst');sc.append(el('cond',delay=0));effect.append(sc);ec=el('childTnLst');effect.append(ec)
    st=el('set');ec.append(st);beh=el('cBhvr');st.append(beh);tim=el('cTn',id=base+2,dur=1,fill='hold');beh.append(tim);tc=el('stCondLst');tc.append(el('cond',delay=0));tim.append(tc);target=el('tgtEl');target.append(el('spTgt',spid=spid));beh.append(target);attrs=el('attrNameLst');a=el('attrName');a.text='style.visibility';attrs.append(a);beh.append(attrs);to=el('to');to.append(el('strVal',val='visible'));st.append(to)
for tag,evt in [('prevCondLst','onPrev'),('nextCondLst','onNext')]:
    c=el(tag);cond=el('cond',evt=evt,delay=0);target=el('tgtEl');target.append(el('sldTgt'));cond.append(target);c.append(cond);seq.append(c)
r.append(t);data['ppt/slides/slide2.xml']=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in data.items():z.writestr(n,b)
print('Added three click-to-appear effects on slide 2.')
