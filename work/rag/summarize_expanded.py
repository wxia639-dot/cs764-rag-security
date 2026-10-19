from pathlib import Path
import json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[2];O=R/'work/expanded'
rows=[json.loads(x) for x in (O/'responses.jsonl').read_text(encoding='utf8').splitlines()]
assert len(rows)==1188
methods=['Unfiltered','Rules','BERT probe','Two signals'];rng=np.random.default_rng(764)
draws=rng.integers(0,33,(1000,33))
def wilson(k,n):
    z=1.96;p=k/n;d=1+z*z/n;c=(p+z*z/2/n)/d;h=z*((p*(1-p)/n+z*z/4/n/n)**.5)/d
    return [max(0,c-h),min(1,c+h)]
metrics={};vectors={}
for name in methods:
    c=[x for x in rows if x['method']==name and x['scenario']=='clean'];a=[x for x in rows if x['method']==name and x['scenario']=='attacked'];assert len(c)==33 and len(a)==264
    av=np.array([np.mean([x['attack_success'] for x in a if x['case']==i]) for i in range(33)]);qv=np.array([np.mean([x['correct'] for x in a if x['case']==i]) for i in range(33)]);cv=np.array([next(x['correct'] for x in c if x['case']==i) for i in range(33)]);anyv=np.array([any(x['attack_success'] for x in a if x['case']==i) for i in range(33)])
    vectors[name]=(av,qv,cv)
    mm={'attack_n':264,'attack_successes':sum(x['attack_success'] for x in a),'asr':float(av.mean()),'clean_n':33,'clean_correct':sum(x['correct'] for x in c),'clean_accuracy':float(cv.mean()),'attacked_correct':sum(x['correct'] for x in a),'attacked_accuracy':float(qv.mean()),'exposed_n':sum(x['attack_exposed'] for x in a),'marker_retained':sum(x['attack_retained'] for x in a),'attacked_abstentions':sum(x['gate_abstention'] for x in a),'clean_abstentions':sum(x['gate_abstention'] for x in c),'emails_with_any_success':int(anyv.sum()),'any_success_wilson95':wilson(int(anyv.sum()),33),'clean_wilson95':wilson(int(cv.sum()),33),'asr_cluster_ci95':np.quantile(av[draws].mean(1),[.025,.975]).tolist(),'attack_accuracy_cluster_ci95':np.quantile(qv[draws].mean(1),[.025,.975]).tolist(),'by_template_position':{f'{t}-{p}':{'successes':sum(x['attack_success'] for x in a if x['template']==t and x['position']==p),'correct':sum(x['correct'] for x in a if x['template']==t and x['position']==p),'n':33} for t in range(4) for p in ['prefix','suffix']}}
    for label in ['answerable','unknown']:
        cc=[x for x in c if (x['ideal']=='unknown')==(label=='unknown')];mm[label+'_n']=len(cc);mm[label+'_correct']=sum(x['correct'] for x in cc)
    metrics[name]=mm
for n in methods[1:]:
    delta=vectors[n][0]-vectors['Unfiltered'][0];metrics[n]['paired_asr_change']=float(delta.mean());metrics[n]['paired_asr_change_ci95']=np.quantile(delta[draws].mean(1),[.025,.975]).tolist()
res={'metrics':metrics,'requests':len(rows),'generation_reused':sum(x.get('generation_reused',False) for x in rows),'actual_generator_calls':sum(not x.get('generation_reused',False) and not x['gate_abstention'] for x in rows),'empty_context_fallbacks':sum(x['gate_abstention'] for x in rows),'source_clusters':33,'responses_sha256':hashlib.sha256((O/'responses.jsonl').read_bytes()).hexdigest(),'scope':'Fixed source/attack crossing; exact generation reuse; latency comparison uses separate uncached pilot'}
(O/'results.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
