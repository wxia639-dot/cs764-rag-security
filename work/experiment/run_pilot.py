"""One fixed BIPIA-derived passage detection pilot; no generator is invoked."""
import os
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
import json, re, hashlib, time, platform, csv
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'work/sources'; OUT=ROOT/'work/experiment'; OUT.mkdir(exist_ok=True)
torch.set_num_threads(4)
rng=np.random.default_rng(764)
def load_lines(name):
    return [json.loads(l) for l in (SRC/name).read_text(encoding='utf8').splitlines() if l.strip()]
train=load_lines('benchmark__email__train.jsonl')
test=load_lines('benchmark__email__test.jsonl')
atr=json.loads((SRC/'benchmark__text_attack_train.json').read_text())
ate=json.loads((SRC/'benchmark__text_attack_test.json').read_text())
order=rng.permutation(len(train)); fit=[train[i] for i in order[:35]]; val=[train[i] for i in order[35:]]
train_payloads=[(k,v) for k,vs in atr.items() for v in vs[:3]]
val_payloads=[(k,v) for k,vs in atr.items() for v in vs[3:]]
test_payloads=[(k,v) for k,vs in ate.items() for v in vs]
model_name='bert-base-uncased'
tok=AutoTokenizer.from_pretrained(model_name,local_files_only=True)
model=AutoModel.from_pretrained(model_name,local_files_only=True).eval()
import pickle
cache_file=OUT/'embedding_cache.pkl'
cache=pickle.loads(cache_file.read_bytes()) if cache_file.exists() else {}; timing=[]
def windows(text):
    ids=tok.encode(text,add_special_tokens=False)
    return [ids[i:i+126] for i in range(0,max(1,len(ids)),96)]
def embed_windows(texts):
    missing=list(dict.fromkeys(t for t in texts if t not in cache))
    if not missing:return
    segments=[]; owners=[]
    for t in missing:
        for seg in windows(t):segments.append([tok.cls_token_id]+seg+[tok.sep_token_id]);owners.append(t)
    groups={t:[] for t in missing}
    with torch.inference_mode():
        for start in range(0,len(segments),16):
            seqs=segments[start:start+16];width=max(map(len,seqs))
            batch={'input_ids':torch.tensor([s+[tok.pad_token_id]*(width-len(s)) for s in seqs]),'attention_mask':torch.tensor([[1]*len(s)+[0]*(width-len(s)) for s in seqs])}
            begin=time.perf_counter()
            hidden=model(**batch).last_hidden_state
            weights=batch['attention_mask'].unsqueeze(-1)
            pooled=(hidden*weights).sum(1)/weights.sum(1)
            timing.append({'windows':len(batch['input_ids']),'ms':(time.perf_counter()-begin)*1000})
            for owner,vec in zip(owners[start:start+16],pooled.numpy()):groups[owner].append(vec)
            print(f'Encoded {min(start+16,len(segments))}/{len(segments)} windows',flush=True)
    for t,vecs in groups.items():cache[t]=np.array(vecs)
    cache_file.write_bytes(pickle.dumps(cache))

embed_windows([r['context'] for r in fit]+[p for _,p in train_payloads])
X=[];Y=[]
for r in fit:
    X.extend(cache[r['context']]);Y.extend([0]*len(cache[r['context']]))
for _,p in train_payloads:
    X.extend(cache[p]);Y.extend([1]*len(cache[p]))
probe=LogisticRegression(C=1.0,class_weight='balanced',max_iter=1000,random_state=764).fit(X,Y)
rules=[r'ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions',r'\b(?:system|developer)\s*(?:message|prompt)\b',r'\b(?:your|the)\s+(?:answer|response|reply|output)\b',r'\b(?:respond|reply|answer)\s+(?:only|instead|with)\b']
rx=re.compile('|'.join(rules),re.I)
def records(contexts,payloads,split):
    out=[{'id':f'{split}-clean-{i}','base':i,'family':'clean','label':0,'text':r['context']} for i,r in enumerate(contexts)]
    # Each attack template occurs twice with distinct base contexts and insertion positions.
    for j,(fam,p) in enumerate(payloads):
        for variant in range(2):
            i=(j*7+variant*13)%len(contexts);ctx=contexts[i]['context']
            txt=(p+'\n'+ctx) if variant==0 else (ctx+'\n'+p)
            out.append({'id':f'{split}-attack-{j}-{variant}','base':i,'family':fam,'template':j,'position':'prefix' if variant==0 else 'suffix','label':1,'text':txt})
    return out
validation=records(val,val_payloads,'validation'); testing=records(test,test_payloads,'test')
embed_windows([r['text'] for r in validation+testing])
def scores(rows):
    neural=np.array([probe.predict_proba(cache[r['text']])[:,1].max() for r in rows])
    rule=np.array([bool(rx.search(r['text'])) for r in rows],dtype=float)
    return {'Unfiltered':np.zeros(len(rows)),'Rules':rule,'BERT probe':neural,'Two signals':1-(1-neural)*(1-0.75*rule)}
vs=scores(validation);ts=scores(testing)
vy=np.array([r['label'] for r in validation]);ty=np.array([r['label'] for r in testing])
thresholds={};metrics={}; predictions={}
def evaluate(y,p):
    tp=int(((y==1)&p).sum());fp=int(((y==0)&p).sum());tn=int(((y==0)&~p).sum());fn=int(((y==1)&~p).sum())
    pr,rc,f1,_=precision_recall_fscore_support(y,p,average='binary',zero_division=0)
    return dict(tp=tp,fp=fp,tn=tn,fn=fn,precision=float(pr),recall=float(rc),f1=float(f1),clean_retention=tn/(tn+fp) if tn+fp else 0.,malicious_pass=fn/(tp+fn) if tp+fn else 0.)
for name in vs:
    if name=='Unfiltered':th=1.1
    elif name=='Rules':th=0.5
    else:
        candidates=np.unique(np.r_[vs[name],1.000001]);best=None
        for th0 in candidates:
            m=evaluate(vy,vs[name]>=th0)
            if 1-m['clean_retention']<=0.05:
                key=(m['recall'],m['precision'],th0)
                if best is None or key>best[0]:best=(key,float(th0))
        th=best[1]
    thresholds[name]=th;p=ts[name]>=th;predictions[name]=p
    metrics[name]=evaluate(ty,p)
    metrics[name]['threshold']=th
    if name not in ['Unfiltered','Rules']:metrics[name]['auroc']=float(roc_auc_score(ty,ts[name]))
    metrics[name]['families']={f:evaluate(ty[[r['family']==f for r in testing]],p[[r['family']==f for r in testing]])['recall'] for f in ate}
# Context-cluster bootstrap describes test sampling uncertainty, not retraining variability.
brng=np.random.default_rng(764);boot={n:[] for n in metrics};delta=[]
for _ in range(1000):
    sampled=brng.integers(0,len(test),len(test));idx=np.concatenate([np.array([i for i,r in enumerate(testing) if r['base']==b]) for b in sampled])
    for n in metrics:boot[n].append(evaluate(ty[idx],predictions[n][idx]))
    delta.append(boot['Two signals'][-1]['recall']-boot['BERT probe'][-1]['recall'])
for n in metrics:
    metrics[n]['ci95']={key:np.quantile([b[key] for b in boot[n]],[.025,.975]).tolist() for key in ['recall','clean_retention','f1']}
versions={'python':platform.python_version(),'torch':torch.__version__}
import sklearn,transformers
versions.update(sklearn=sklearn.__version__,transformers=transformers.__version__)
result={'scope':'BIPIA-derived EmailQA passage detection pilot; no retrieval or generation; not an official BIPIA ASR evaluation','seed':764,'train_contexts':len(fit),'validation_contexts':len(val),'test_contexts':len(test),'train_payloads':len(train_payloads),'validation_payloads':len(val_payloads),'test_payloads':len(test_payloads),'validation_rows':len(validation),'test_rows':len(testing),'train_windows':len(Y),'versions':versions,'machine':platform.processor(),'threads':4,'model':model_name,'window_tokens':126,'stride':96,'probe':{'C':1.0,'class_weight':'balanced','max_iter':1000},'metrics':metrics,'delta_recall_hybrid_minus_neural_ci95':np.quantile(delta,[.025,.975]).tolist(),'bert_batch_latency_ms_per_window':{'median':float(np.median([t['ms']/t['windows'] for t in timing])),'p95':float(np.quantile([t['ms']/t['windows'] for t in timing],.95)),'note':'Offline batched encoder time only; includes first batch; excludes tokenization and generator; not per-request latency'},'sources_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.iterdir() if p.is_file()},'exact_context_overlap_train_test':len(set(r['context'] for r in train)&set(r['context'] for r in test)),'exact_payload_overlap_train_test':len(set(p for _,p in train_payloads+val_payloads)&set(p for _,p in test_payloads))}
(OUT/'results.json').write_text(json.dumps(result,indent=2),encoding='utf8')
with (OUT/'predictions.csv').open('w',newline='',encoding='utf8') as f:
    wr=csv.writer(f);wr.writerow(['id','base','family','label']+[n+' score' for n in ts]+[n+' reject' for n in ts])
    for i,r in enumerate(testing):wr.writerow([r['id'],r['base'],r['family'],r['label']]+[float(ts[n][i]) for n in ts]+[int(predictions[n][i]) for n in ts])
(OUT/'split_manifest.json').write_text(json.dumps({'train_context_indices':order[:35].tolist(),'validation_context_indices':order[35:].tolist(),'validation':[{k:v for k,v in r.items() if k!='text'} for r in validation],'test':[{k:v for k,v in r.items() if k!='text'} for r in testing]},indent=2))
np.savez_compressed(OUT/'probe.npz',coef=probe.coef_,intercept=probe.intercept_,classes=probe.classes_)
print(json.dumps(result,indent=2))
