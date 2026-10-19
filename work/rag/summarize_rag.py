"""Analysis only of the completed fixed experiment; no model execution."""
import json,hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
r=json.loads((P/'results.json').read_text());rows=[json.loads(x) for x in (P/'responses.jsonl').read_text().splitlines()]
lookup={(x['case'],x['scenario'],x['method']):x for x in rows};rng=np.random.default_rng(764)
comparisons={}
for method in ['Rules','BERT probe','Two signals']:
    metrics={}
    for name,scenario,key in [('attack_success_change','attacked','attack_success'),('clean_accuracy_change','clean','correct'),('attacked_accuracy_change','attacked','correct')]:
        delta=np.array([int(lookup[j,scenario,method][key])-int(lookup[j,scenario,'Unfiltered'][key]) for j in range(16)])
        sims=delta[rng.integers(0,16,size=(1000,16))].mean(1)
        metrics[name]={'point':float(delta.mean()),'ci95':np.quantile(sims,[.025,.975]).tolist()}
    comparisons[method]=metrics
r['paired_query_bootstrap']=comparisons
r['generator_invocations']=sum(not x['gate_abstention'] for x in rows)
r['total_requests']=len(rows)
examples=[]
predicates=[('Suppressed marker attack',lambda b,h:b['attack_success'] and not h['attack_success']),('Answering trade-off',lambda b,h:b['correct'] and not h['correct']),('Residual marker attack',lambda b,h:h['attack_success'])]
for label,predicate in predicates:
    found=[]
    for j in range(16):
        b=lookup[j,'attacked','Unfiltered'];h=lookup[j,'attacked','Two signals']
        if predicate(b,h):found.append({'label':label,'case':j,'ideal':b['ideal'],'unfiltered':b['response'],'two_signals':h['response'],'unfiltered_correct':b['correct'],'two_signals_correct':h['correct'],'hybrid_gate_abstention':h['gate_abstention']})
    if found:examples.append(found[0])
for j in range(16):
    b=lookup[j,'clean','Unfiltered'];h=lookup[j,'clean','Two signals']
    if b['ideal']=='unknown' and not b['correct'] and not h['correct']:
        examples.append({'label':'Clean unanswerable error','case':j,'ideal':b['ideal'],'unfiltered':b['response'],'two_signals':h['response']});break
r['illustrative_examples']=examples
r['source_sha256']={name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in ['run_rag.py','PROTOCOL.md','config.json','case_manifest.json','responses.jsonl']}
weights=P.parent/'models/qwen-0.5b/model.safetensors'
h=hashlib.sha256()
with weights.open('rb') as f:
    while True:
        b=f.read(8*1024*1024)
        if not b:break
        h.update(b)
r['generator_weights_sha256']=h.hexdigest()
(P/'results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
