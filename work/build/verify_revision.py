from pathlib import Path
import json,zipfile,hashlib,re
from pypdf import PdfReader
R=Path(__file__).resolve().parents[2];O=R/'outputs'
pdf=PdfReader(O/'CS764_RAG_Security_Report_Revised.pdf');text='\n'.join(p.extract_text() or '' for p in pdf.pages)
assert len(pdf.pages)==11
assert 'REFERENCES' in pdf.pages[-1].extract_text().upper()
assert not any('REFERENCES' in p.extract_text().upper()[:60] for p in pdf.pages[:-1])
for s in ['AI-assisted working draft','The teacher recommended','preceding literature review','Individual contributions are deliberately not assigned']:assert s not in text,s
assert '102/264' in text and '7/264' in text and '24/24' in text
raw=[json.loads(x) for x in (R/'work/expanded/responses.jsonl').read_text(encoding='utf8').splitlines()]
assert len(raw)==1188
assert len({(x['case'],x['scenario'],x['template'],x['position'],x['method']) for x in raw})==1188
for name,success,clean,attacked in [('Unfiltered',102,16,71),('Rules',16,16,117),('BERT probe',85,16,83),('Two signals',7,16,125)]:
    a=[x for x in raw if x['method']==name and x['scenario']=='attacked'];c=[x for x in raw if x['method']==name and x['scenario']=='clean']
    assert len(a)==264 and len(c)==33
    assert sum(x['attack_success'] for x in a)==success
    assert sum(x['correct'] for x in a)==attacked
    assert sum(x['correct'] for x in c)==clean
with zipfile.ZipFile(O/'CS764_RAG_Security_Presentation_Revised.pptx') as z:
    assert z.testzip() is None
    slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)];assert len(slides)==12
    allslides=''.join(z.read(n).decode('utf8') for n in slides)
    assert 'working draft' not in allslides.lower()
    assert '102' in allslides and '264' in allslides and '24/24' in allslides
receipt=json.loads((R/'work/build/presentation.revised.v2.validation.json').read_text());assert receipt['finalSha256']==hashlib.sha256((O/'CS764_RAG_Security_Presentation_Revised.pptx').read_bytes()).hexdigest()
with zipfile.ZipFile(O/'CS764_RAG_Security_Report_Revised.docx') as z:
    assert z.testzip() is None;xml=z.read('word/document.xml').decode('utf8');assert xml.count('<m:oMath>')==3
with zipfile.ZipFile(O/'CS764_Code_and_Results_Revised.zip') as z:
    assert z.testzip() is None
    assert z.read('work/expanded/responses.jsonl')==(R/'work/expanded/responses.jsonl').read_bytes()
    assert z.read('work/ieee_report/main.tex')==(R/'work/ieee_report/main.tex').read_bytes()
    assert not any('model.safetensors' in n or '/runtime/' in n for n in z.namelist())
notes=json.loads((R/'work/build/revised_speaker_notes.json').read_text());assert sum(x['seconds'] for x in notes[:6])==270 and sum(x['seconds'] for x in notes[6:])==270
names=['CS764_RAG_Security_Report_Revised.pdf','CS764_RAG_Security_Report_Revised.docx','CS764_RAG_Security_Presentation_Revised.pptx','CS764_Presentation_Script_Revised.md','CS764_Code_and_Results_Revised.zip','CS764_IEEE_LaTeX_Source.zip','CS764_贡献说明_已确认.md','CS764_审阅意见逐项处理.md','CS764_修订版阅读说明.md']
manifest={n:{'bytes':(O/n).stat().st_size,'sha256':hashlib.sha256((O/n).read_bytes()).hexdigest()} for n in names}
(O/'CS764_Revised_Manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(R/'work/build/revised_final_check.json').write_text(json.dumps({'report_pages':11,'body_pages':10,'references_pages':1,'slides':12,'speaker_seconds':[270,270],'requests':1188,'verification':'Counts, package integrity, exact archive/raw matches, mathematical objects, absence of draft header; visual inspection recorded separately.','files':manifest},indent=2),encoding='utf8')
print('PASS: 10 body pages + 1 reference page; 12 slides; 1188 unique logged decisions; archive/source hashes match.')
