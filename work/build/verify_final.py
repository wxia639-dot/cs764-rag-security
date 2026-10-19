from final_content import *
from pypdf import PdfReader
import zipfile,re,hashlib
O=ROOT/'outputs';pdf=PdfReader(O/'CS764_RAG_Security_Report_Final.pdf');txt='\n'.join(p.extract_text() or '' for p in pdf.pages)
assert len(pdf.pages)==12
for bad in ['TABLE_REF','AI-assisted working draft','Individual contributions are deliberately not assigned','The teacher recommended','preceding literature review','require author verification']:
    assert bad not in txt,bad
assert 'Weiyi Xia is responsible' in txt and 'Xinye He is responsible' in txt
assert '0.415' in txt and '28/37' in txt
with zipfile.ZipFile(O/'CS764_RAG_Security_Presentation_Final.pptx') as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)])==12
    assert len([n for n in z.namelist() if n.startswith('ppt/media/')])>=2
    notes=''.join(z.read(n).decode() for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n))
    assert 'Evidence:' not in notes and 'work/expanded/' not in notes
with zipfile.ZipFile(O/'CS764_Code_and_Results_Final.zip') as z:
    assert z.testzip() is None
    for p in ['work/expanded/responses.jsonl','work/deberta_audit/results.json','work/rag/CONTRIBUTIONS.md','work/ieee_report/main.tex']:
        assert z.read(p)==(ROOT/p).read_bytes(),p
check={'report_pages':12,'body_pages':11,'references_pages':1,'abstract_words':len(ABSTRACT.split()),'references':len(REFERENCES),'slides':12,'speaker_seconds':[270,270],'deberta_direct_512_auroc':A512['auroc'],'checks':'Final text, contributions, embedded figure bytes, notes, archives and unchanged raw results; selected pages and all slide montage inspected visually.'}
(ROOT/'work/build/final_check.json').write_text(json.dumps(check,indent=2))
print(json.dumps(check))
