from final_content import *
import zipfile,shutil,hashlib
OUT=ROOT/'outputs'; STAGE=ROOT/'work/public_repository';STAGE.mkdir(exist_ok=True)
lines=['# Author responsibilities','','The authors supplied the following allocation. These are agreed responsibilities, including AI-assisted work, rather than a claim of unaided authorship or completed recording/submission.','','| Item | Responsibility | Author |','|---|---|---|']
for i,item in enumerate(CONTRIBUTIONS,1):
    owner='Both authors' if i>=17 else ('Weiyi Xia' if i%2 else 'Xinye He')
    lines.append(f'| {i} | {item} | {owner} |')
lines+=['',AI_TEXT]
ct='\n'.join(lines)+'\n'
(ROOT/'work/rag/CONTRIBUTIONS.md').write_text(ct,encoding='utf8')
(OUT/'CS764_Contributions_Final.md').write_text(ct,encoding='utf8')
old=(ROOT/'work/github_upload/README.md').read_text(encoding='utf8')
readme=old.replace('_Revised','_Final').replace('CS764_IEEE_LaTeX_Source.zip','CS764_IEEE_LaTeX_Source_Final.zip')
readme=readme.replace('Extract the complete source archive in a new directory.','Clone this repository, or extract the source archive in a new directory. The actual `work/` source and raw result directories are included directly in the repository.')
readme=readme.replace('python work/rag/run_revision_detection.py','python work/rag/run_revision_detection.py\npython work/rag/audit_deberta.py')
start=readme.index('The authors declared Weiyi Xia responsible')
readme=readme[:start]+'Weiyi Xia is responsible for odd-numbered items 1–16, Xinye He for even-numbered items 1–16; items 17–18 are shared. See [the full English responsibilities](work/rag/CONTRIBUTIONS.md) and the concrete descriptions in the final report. '+AI_TEXT+' Recording and Canvas submission are not completed by this archive.\n'
readme+='''
## Second-review baseline audit

The pinned checkpoint really maps SAFE=0 and INJECTION=1, and neutral/explicit-injection controls confirm this direction. Direct published-style 512-token truncation gives 68/111 attack detections and 28/37 clean false rejections, AUROC 0.415; none of these original 148 passages is truncated. The historical 126-token-window condition remains separately reported (73/111, 31/37, AUROC 0.430). Four controlled marker payloads score above 0.998; six standalone public payloads score below 0.001, while four unmodified financial emails score above 0.98. This supports a domain/task-context mismatch interpretation, without proving a unique cause. Protocol, logits, scores and examples are in `work/deberta_audit/`.

Final report: 11 body pages plus one reference page; 157-word abstract; 18 references. Final presentation: 12 slides, approximately nine minutes, equal speaking time. Historical Revised files may remain in Git history; filenames ending in Final are current.
'''
readme=readme.replace('12-slide','14-slide').replace('12 slides','14 slides')+'\nThe current presentation has 14 slides and a 1,011-word English script, with 270 seconds assigned to each speaker. Its source entry point is work/build/build_visual_deck.mjs; prepare_visual_deck.py binds the recorded data and script, and animate_visual_deck.py adds three click-to-appear effects on slide 2. The presentation uses editable shapes for charts and diagrams, with a minimum text size of 21 pt.\n'
(ROOT/'work/rag/README_FINAL.md').write_text(readme,encoding='utf8')
files=[]
allowed={'.py','.json','.jsonl','.csv','.npz','.md','.txt','.tex','.cls','.pdf','.svg','.png'}
for folder in ['experiment','rag','expanded','revision_detection','deberta_audit','sources','ieee_report']:
    for p in (ROOT/'work'/folder).rglob('*'):
        if p.is_file() and (p.suffix in allowed or p.name=='LICENSE') and '__pycache__' not in p.parts and p.name not in ['main.pdf','README_REVISED.md','README_UPDATED.md']:
            files.append(p)
for p in (ROOT/'work/build').iterdir():
    if p.is_file() and p.suffix in ['.py','.mjs','.json'] and ('revision' in p.name or 'revised' in p.name or 'final' in p.name or 'visual' in p.name or p.name in ['completed_content.py','report_content.py','plot_slide_security.py']):files.append(p)
files += [ROOT/'work/build/reference_audit.md',ROOT/'work/requirements-revision.txt',ROOT/'work/requirements-pilot.txt',ROOT/'work/download_models.py']
for p in sorted(set(files)):
    q=STAGE/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(STAGE/'README.md').write_text(readme,encoding='utf8')
for name in ['requirements-revision.txt','requirements-pilot.txt']:shutil.copy2(ROOT/'work'/name,STAGE/name)
for name in ['CS764_RAG_Security_Report_Final.pdf','CS764_RAG_Security_Presentation_Final.pptx','CS764_Presentation_Script_Final.md']:shutil.copy2(OUT/name,STAGE/name)
with zipfile.ZipFile(OUT/'CS764_Code_and_Results_Final.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(STAGE.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(STAGE).as_posix())
with zipfile.ZipFile(OUT/'CS764_IEEE_LaTeX_Source_Final.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in (ROOT/'work/ieee_report').rglob('*'):
        if p.is_file() and p.suffix in ['.tex','.cls','.pdf','.svg','.png'] and p.name!='main.pdf':z.write(p,p.relative_to(ROOT/'work/ieee_report').as_posix())
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.iterdir() if p.is_file() and 'Final' in p.name}
(OUT/'CS764_Final_Manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
groups={}
for p in sorted(STAGE.rglob('*')):
    if p.is_file():groups.setdefault(p.parent.relative_to(STAGE).as_posix(),[]).append(str(p))
(ROOT/'work/build/upload_groups.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:len(v) for k,v in groups.items()}))



