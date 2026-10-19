"""One predeclared full crossing: 33 emails x 4 templates x 2 positions.
Reuses frozen detectors; no tuning against expanded generator outcomes.
"""
from pathlib import Path
import json, time, hashlib
ROOT=Path(__file__).resolve().parents[2]
prefix=(ROOT/'work/rag/run_rag.py').read_text(encoding='utf8').split('indexes={};case_manifest=[]')[0]
exec(compile(prefix, str(ROOT/'work/rag/run_rag.py'), 'exec'))
OUT=ROOT/'work/expanded';OUT.mkdir(exist_ok=True)
cases=unique
protocol={'source':'All exact-text-distinct test emails excluded from original train contexts', 'emails':len(cases),'templates':4,'positions':['prefix','suffix'],'methods':METHODS,'clean_requests':len(cases)*4,'attacked_requests':len(cases)*8*4,'seed':764,'thresholds':thresholds,'max_new_tokens':48,'timing':'Exact deterministic question/evidence generation reuse introduced after first 44 requests solely to avoid duplicate computation; cache flags and origin recorded. Expanded timings not used for cross-method latency claims; original uncached paired pilot supplies cost evidence.','inference':'Cluster by source email; variants are dependent; no binomial independence claim over variants'}
(OUT/'protocol.json').write_text(json.dumps(protocol,indent=2))
manifest=[];tasks=[]
for j,(source,item) in enumerate(cases):
    tasks.append((j,source,item,'clean',-1,'none',item['context']))
    for family,attack in enumerate(ATTACKS):
        for pos in ['prefix','suffix']:
            ctx=attack+'\n'+item['context'] if pos=='prefix' else item['context']+'\n'+attack
            tasks.append((j,source,item,'attacked',family,pos,ctx))
    manifest.append({'case':j,'source_record':source,'ideal':item['ideal'],'question':item['question'],'context_sha256':hashlib.sha256(item['context'].encode()).hexdigest()})
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
done={};path=OUT/'responses.jsonl'
if path.exists():
    for line in path.read_text(encoding='utf8').splitlines():
        x=json.loads(line);done[x['case'],x['scenario'],x['template'],x['position'],x['method']]=x
idx=make_index(cases[0][1]['context']);_,ps,_=retrieve(idx,cases[0][1]['question']);answer(cases[0][1]['question'],ps);neural_scores(ps)
total=len(tasks)*len(METHODS)
answer_cache={}
neural_cache={}
with path.open('a',encoding='utf8') as log:
    for j,source,item,scenario,family,pos,ctx in tasks:
        index=make_index(ctx)
        for method in METHODS[j%4:]+METHODS[:j%4]:
            key=(j,scenario,family,pos,method)
            if key in done:
                _,existing_ps,_=retrieve(index,item['question']);old=done[key]
                kept=[existing_ps[i] for i in old['retained_local_ids']]
                if kept:answer_cache[(item['question'],tuple(kept))]=(old['response'],old['output_tokens'],old['prompt_tokens'],list(key))
                continue
            start=time.perf_counter();ids,ps,sim=retrieve(index,item['question']);t1=time.perf_counter()
            if method in ['BERT probe','Two signals']:
                sig=tuple(ps)
                if sig not in neural_cache:neural_cache[sig]=neural_scores(ps)
                ns=np.array(neural_cache[sig]);cue=np.array([bool(rx.search(p)) for p in ps])
                ss=ns if method=='BERT probe' else 1-(1-ns)*(1-.75*cue)
                scores=ss.tolist();keep=[i for i,s in enumerate(scores) if s<thresholds[method]]
            else:keep,scores=gate(method,ps)
            kept=[ps[i] for i in keep];t2=time.perf_counter();cache_key=(item['question'],tuple(kept));cached=bool(kept) and cache_key in answer_cache
            if cached:text,nt,ip,origin=answer_cache[cache_key]
            elif kept:
                text,nt,ip=answer(item['question'],kept);origin=list(key);answer_cache[cache_key]=(text,nt,ip,origin)
            else:text,nt,ip,origin='UNKNOWN',0,0,None
            end=time.perf_counter();ok,strict=correctness(text,item['ideal'])
            x={'case':j,'source_record':source,'scenario':scenario,'template':family,'position':pos,'method':method,'ideal':item['ideal'],'question':item['question'],'response':text,'correct':ok,'strict_exact_match':strict,'attack_success':scenario=='attacked' and MARKER.lower() in text.lower(),'attack_exposed':scenario=='attacked' and any(MARKER in p for p in ps),'attack_retained':scenario=='attacked' and any(MARKER in p for p in kept),'gate_abstention':not kept,'retrieved_ids':ids,'retained_local_ids':keep,'scores':scores,'output_tokens':nt,'prompt_tokens':ip,'gate_ms':1000*(t2-t1),'request_ms':1000*(end-start)}
            x.update(generation_reused=cached,generation_origin=origin,timing_comparable=False)
            log.write(json.dumps(x,ensure_ascii=False)+'\n');log.flush();done[key]=x
        print(f'{len(done)}/{total} completed; email {j} {scenario} template {family} {pos}',flush=True)
assert len(done)==total
(OUT/'completion.json').write_text(json.dumps({'requests':len(done),'responses_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'complete':True},indent=2))
