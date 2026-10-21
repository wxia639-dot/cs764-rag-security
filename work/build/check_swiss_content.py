from pathlib import Path
from collections import Counter
from lxml import etree as E
import zipfile,re,json
R=Path(__file__).resolve().parents[2];ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
old=zipfile.ZipFile(R/'work/build/content_locked_before_swiss.pptx');new=zipfile.ZipFile(R/'outputs/CS764_RAG_Security_Presentation_Final.pptx')
changes=[]
for i in range(1,15):
    def tokens(z):
        r=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'));txt=' '.join(r.xpath('//a:t/text()',namespaces=ns))
        return Counter(re.findall(r'\w+|[^\w\s]',txt))
    a,b=tokens(old),tokens(new)
    if a!=b:changes.append({'slide':i,'missing':list((a-b).elements()),'extra':list((b-a).elements())})
    assert old.read(f'ppt/notesSlides/notesSlide{i}.xml')==new.read(f'ppt/notesSlides/notesSlide{i}.xml'),f'Notes changed on slide {i}'
result={'slides':14,'content_changes':changes,'speaker_notes':'byte-identical','scope':'Slide text tokens, numbers and punctuation unchanged; text can reflow or move within its slide.'}
(R/'work/build/swiss_content_check.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result));assert not changes
