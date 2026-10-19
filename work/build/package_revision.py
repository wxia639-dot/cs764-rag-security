from bind_revised_results import *
import zipfile,hashlib,re
OUT=ROOT/'outputs';G=ROOT/'work/github_upload';G.mkdir(exist_ok=True)
contribution_items=[x.strip() for x in (OUT/'CS764_贡献工作清单_未分配.md').read_text(encoding='utf8').splitlines() if re.match(r'^\d+\.',x)]
contrib=['# 两位作者确认的贡献分工','','按作者确认记录，不分配百分比。第 17–18 项为共同负责事项，录制和提交不标为已完成。','','| 项目 | 工作事项 | 负责人 |','|---|---|---|']
for i,line in enumerate(contribution_items,1):
    owner='Weiyi Xia' if i<=8 else ('Xinye He（何欣叶）' if i<=16 else '两位作者共同负责')
    contrib.append(f'| {i} | {re.sub(r"^\d+\.\s*","",line)} | {owner} |')
contrib+=['','AI 用于代码、执行、分析、写作和幻灯片准备。以上为两位作者声明的责任分配，不表示所有内容均为无 AI 辅助独立完成。报告保留真实的 AI 使用说明。']
ct='\n'.join(contrib);(OUT/'CS764_贡献说明_已确认.md').write_text(ct,encoding='utf8');(ROOT/'work/rag/CONTRIBUTIONS.md').write_text(ct,encoding='utf8')
readme=f'''# CS764 RAG Security

Passage filtering in a document-scoped RAG application. This repository contains the complete reproducibility archive, revised report and presentation. The source archive preserves `work/` directories so the scripts run with their documented paths.

## Contents

- `CS764_Code_and_Results_Revised.zip`: source, public source data and licence, fitted coefficients, all raw outputs, fixed settings, summaries, figures and report/slide authoring sources.
- `CS764_RAG_Security_Report_Revised.pdf`: IEEEtran conference-format report.
- `CS764_RAG_Security_Presentation_Revised.pptx`: editable 12-slide presentation with notes.
- `CS764_IEEE_LaTeX_Source.zip`: editable IEEEtran project and vector figures.

## Findings and limits

The original combination detects 74/111 attacked passages and rejects 0/37 unmodified email records. It rejects **24/24** authored legitimate instruction paragraphs. This is a concrete benign-transfer failure, so the current gate is not recommended for general deployment.

The expanded study uses 33 distinct emails, four fixed marker templates and two positions: 264 attacked variants per gate and 1,188 total decisions. Unfiltered marker successes: {U['attack_successes']}/264; combined: {H['attack_successes']}/264. Clean combined correctness: {H['clean_correct']}/33. Variants are clustered by source email for uncertainty. The expansion reuses exact deterministic question/evidence responses; all reuse origins are logged. Latency uses the separate uncached 16-email pilot.

The external ProtectAI detector uses a pinned checkpoint, maximum 126-token windows at stride 96 and a fixed 0.5 threshold. It is a passage-only reference condition, not an end-to-end system baseline. Mixed-window training improves AUROC but lowers recall at its validation-selected threshold. Neither experiment evaluates adaptive attacks or open-corpus poisoning.

## Reproduce

Extract the complete source archive in a new directory. Use Python 3.12 and install `requirements-revision.txt`. CPU execution is supported; no paid model API or credentials are needed.

```text
python -m pip install -r requirements-revision.txt
python work/download_models.py
python work/experiment/run_pilot.py
python work/experiment/analyze_overlap.py
python work/rag/run_rag.py
python work/rag/run_expanded.py
python work/rag/summarize_expanded.py
python work/rag/run_revision_detection.py
```

Original pilot library versions are recorded separately in `requirements-pilot.txt`. Published raw pilot and expanded results come from distinct executions; compare them using their own configurations, rather than pooling them. To force new output, use a fresh extracted directory and rename the existing response logs before execution. The expansion resumes existing rows by key. All model weights are excluded from the archive.

`work/download_models.py` downloads the original BERT checkpoint, pinned Qwen snapshot and pinned ProtectAI snapshot. The Qwen weight SHA-256 recorded with the experiment is `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`. Weight availability and third-party package compatibility may change; original logs remain the evidence for the reported execution.

## Traceability

- `work/experiment/`: original passage predictions, coefficients, split manifest and overlap audit.
- `work/rag/`: original 128 uncached request outputs and local execution scripts.
- `work/expanded/`: all 1,188 decisions, cache origins, full crossing manifest, protocol and clustered results.
- `work/revision_detection/`: external/mixed probe scores, 24 benign texts, fixed protocol and sensitivity analyses.
- `work/ieee_report/`: actual IEEEtran source and vector figures. Compile `main.tex` with Tectonic or a standard TeX installation.
- `work/build/`: plot script and report/deck authoring code. The Word companion uses Microsoft's local MathML-to-OMML stylesheet; LaTeX is the portable layout source. The editable presentation authoring source uses the Codex bundled Artifact Tool, which is not redistributed.

## Origin and contribution disclosure

Public EmailQA and text-attack data originate from [Microsoft BIPIA](https://github.com/microsoft/BIPIA); its included licence is retained. Retrieval, gates, controlled marker attacks and local scorers are project implementations, not a reproduction of the full official BIPIA multi-model benchmark. Model checkpoints retain their respective licences and official attribution.

The authors declared Weiyi Xia responsible for work items 1–8; Xinye He for 9–16; items 17–18 jointly. AI assistance was used in coding, execution, analysis and drafting; author verification and the recorded disclosure remain necessary. Recording and Canvas submission are not completed by this archive.
'''
(G/'README.md').write_text(readme,encoding='utf8');(ROOT/'work/rag/README_REVISED.md').write_text(readme,encoding='utf8')
revision_requirements='torch==2.14.1\ntransformers==5.20.1\nscikit-learn==1.9.1\nhuggingface-hub==2.2.0\nmatplotlib==3.11.2\nsentencepiece==0.2.2\nreportlab\npython-docx\npypdf\nlxml\n'
(ROOT/'work/requirements-revision.txt').write_text(revision_requirements)
(ROOT/'work/requirements-pilot.txt').write_text('torch==2.13.0\ntransformers==5.15.0\nscikit-learn==1.9.0\n')
download='''from pathlib import Path
import json
from huggingface_hub import snapshot_download
R=Path(__file__).resolve().parents[1]
snapshot_download('bert-base-uncased',allow_patterns=['*.json','model.safetensors','vocab.txt'])
snapshot_download('Qwen/Qwen2.5-0.5B-Instruct',revision='7ae557604adf67be50417f59c2c2f167def9a775',local_dir=R/'work/models/qwen-0.5b',allow_patterns=['*.json','*.txt','*.safetensors','*.model','LICENSE','README.md'])
p=R/'work/models/protectai';sha='90c9989b1a342275dd0d1a95aad283c04e075671'
snapshot_download('protectai/deberta-v3-base-prompt-injection-v2',revision=sha,local_dir=p,allow_patterns=['*.json','spm.model','model.safetensors','README.md','LICENSE'])
(p/'revision.json').write_text(json.dumps({'repo':'protectai/deberta-v3-base-prompt-injection-v2','revision':sha},indent=2))
'''
(ROOT/'work/download_models.py').write_text(download)
files=[]
for folder in ['experiment','rag','expanded','revision_detection','sources','ieee_report']:
    for p in (ROOT/'work'/folder).rglob('*'):
        if p.is_file() and p.suffix in ['.py','.json','.jsonl','.csv','.npz','.md','.log','.txt','.tex','.cls','.pdf','.svg','.png'] and '__pycache__' not in p.parts and p.name not in ['main.pdf','main.log','README.md','README_UPDATED.md']:
            files.append(p)
files.append(ROOT/'work/sources/LICENSE')
for p in (ROOT/'work/build').iterdir():
    if p.is_file() and p.suffix in ['.py','.mjs','.json'] and ('revision' in p.name or 'revised' in p.name or p.name in ['completed_content.py','report_content.py']):files.append(p)
files+=[ROOT/'work/requirements-revision.txt',ROOT/'work/requirements-pilot.txt',ROOT/'work/download_models.py']
files.append(ROOT/'work/build/reference_audit.md')
target=OUT/'CS764_Code_and_Results_Revised.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('README.md',readme);z.write(ROOT/'work/requirements-revision.txt','requirements-revision.txt');z.write(ROOT/'work/requirements-pilot.txt','requirements-pilot.txt')
    for p in sorted(set(files)):z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT/'CS764_IEEE_LaTeX_Source.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in (ROOT/'work/ieee_report').rglob('*'):
        if p.is_file() and p.suffix in ['.tex','.cls','.pdf','.svg','.png'] and p.name!='main.pdf':z.write(p,p.relative_to(ROOT/'work/ieee_report').as_posix())
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.iterdir() if p.is_file() and ('Revised' in p.name or '已确认' in p.name or 'LaTeX' in p.name)}
(OUT/'CS764_Revised_Manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
with zipfile.ZipFile(target) as z:assert z.testzip() is None
print(json.dumps({'files':len(set(files))+3,'zip_bytes':target.stat().st_size,'archive':str(target)}))
