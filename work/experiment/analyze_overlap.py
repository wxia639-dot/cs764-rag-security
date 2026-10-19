"""Post-run overlap audit on existing predictions; no training or model inference."""
import json,csv,pickle,re
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[2];D=R/'work/experiment';S=R/'work/sources'
r=json.loads((D/'results.json').read_text())
train=[json.loads(l) for l in (S/'benchmark__email__train.jsonl').read_text(encoding='utf8').splitlines()]
test=[json.loads(l) for l in (S/'benchmark__email__test.jsonl').read_text(encoding='utf8').splitlines()]
seen={x['context'] for x in train};allowed=[i for i,x in enumerate(test) if x['context'] not in seen]
rows=[x for x in csv.DictReader((D/'predictions.csv').open(encoding='utf8')) if int(x['base']) in allowed]
names=list(r['metrics']); y=np.array([int(x['label']) for x in rows]);pred={n:np.array([int(x[n+' reject']) for x in rows],dtype=bool) for n in names}
def metrics(y,p):
    tp=int(((y==1)&p).sum());fp=int(((y==0)&p).sum());tn=int(((y==0)&~p).sum());fn=int(((y==1)&~p).sum())
    pr=tp/max(1,tp+fp);rc=tp/max(1,tp+fn)
    return dict(tp=tp,fp=fp,tn=tn,fn=fn,precision=pr,recall=rc,f1=2*pr*rc/max(1e-12,pr+rc),clean_retention=tn/max(1,tn+fp),malicious_pass=fn/max(1,tp+fn))
manifest=json.loads((D/'split_manifest.json').read_text());fc={train[i]['context'] for i in manifest['train_context_indices']};vc={train[i]['context'] for i in manifest['validation_context_indices']}
# Remove fitting-context copies from validation too. Use cached representations; no encoder calls.
vcontexts=[train[i] for i in manifest['validation_context_indices']]
vbank=json.loads((S/'benchmark__text_attack_train.json').read_text());vp=[(k,p) for k,ps in vbank.items() for p in ps[3:]]
valid_rows=[]
for x in manifest['validation']:
    if vcontexts[x['base']]['context'] in fc:continue
    ctx=vcontexts[x['base']]['context']
    if x['label']:
        payload=vp[x['template']][1];txt=payload+'\n'+ctx if x['position']=='prefix' else ctx+'\n'+payload
    else:txt=ctx
    valid_rows.append((x,txt))
cache=pickle.loads((D/'embedding_cache.pkl').read_bytes());z=np.load(D/'probe.npz');a=z['coef'][0];b=z['intercept'][0]
regex=re.compile(r'ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions|\b(?:system|developer)\s*(?:message|prompt)\b|\b(?:your|the)\s+(?:answer|response|reply|output)\b|\b(?:respond|reply|answer)\s+(?:only|instead|with)\b',re.I)
neural=np.array([float((1/(1+np.exp(-(cache[t]@a+b)))).max()) for _,t in valid_rows]);cue=np.array([bool(regex.search(t)) for _,t in valid_rows]);vy=np.array([x['label'] for x,t in valid_rows])
vs={'BERT probe':neural,'Two signals':1-(1-neural)*(1-.75*cue)};thresholds={}
for n in names:
    th=r['metrics'][n]['threshold']
    if n in vs:
        best=None
        for th0 in np.unique(np.r_[vs[n],1.000001]):
            m=metrics(vy,vs[n]>=th0)
            if 1-m['clean_retention']<=.05:
                key=(m['recall'],m['precision'],th0)
                if best is None or key>best[0]:best=(key,float(th0))
        th=best[1]
    thresholds[n]=th
    pred[n]=np.array([float(x[n+' score'])>=th for x in rows])
ms={n:metrics(y,pred[n]) for n in names};rng=np.random.default_rng(764);boot={n:[] for n in names};diff=[]
unique_contexts=list(dict.fromkeys(test[i]['context'] for i in allowed))
group_indices=[np.array([j for j,x in enumerate(rows) if test[int(x['base'])]['context']==ctx]) for ctx in unique_contexts]
for _ in range(1000):
    idx=np.concatenate([group_indices[b] for b in rng.integers(0,len(group_indices),len(group_indices))])
    for n in names:boot[n].append(metrics(y[idx],pred[n][idx]))
    diff.append(boot['Two signals'][-1]['recall']-boot['BERT probe'][-1]['recall'])
for n in names:
    ms[n]['ci95']={k:np.quantile([b[k] for b in boot[n]],[.025,.975]).tolist() for k in ['recall','clean_retention','f1']}
    ms[n]['threshold']=thresholds[n]
    ms[n]['families']={f:metrics(y[[x['family']==f for x in rows]],pred[n][[x['family']==f for x in rows]])['recall'] for f in sorted({x['family'] for x in rows if x['family']!='clean'})}
r['disjoint_test']={'reason':'Post-run exact-context-overlap audit; calibration excludes fitting copies; only cached scores used; no new model inference','clean_contexts':len(allowed),'attack_rows':int(y.sum()),'total_rows':len(rows),'allowed_test_indices':allowed,'metrics':ms,'validation_clean_contexts':int((vy==0).sum()),'validation_attack_rows':int(vy.sum()),'delta_recall_hybrid_minus_neural_ci95':np.quantile(diff,[.025,.975]).tolist(),'test_rows_removed':len(test)-len(allowed),'thresholds_changed':{n:thresholds[n]!=r['metrics'][n]['threshold'] for n in names}}
r['fit_validation_exact_overlap']=len(fc&vc)
r['disjoint_test']['unique_clean_contexts']=len(unique_contexts)
r['disjoint_test']['bootstrap_cluster']='Exact email text, not record index; 33 clusters'
(D/'results.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r['disjoint_test'],indent=2));print('fit/validation overlap',r['fit_validation_exact_overlap'])
