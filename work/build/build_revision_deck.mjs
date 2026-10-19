import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from 'file:///C:/Users/惠普/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const root=path.resolve('.'),out=path.join(root,'outputs'),build=path.join(root,'work/build');
const skill='C:/Users/惠普/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const python='C:/Users/惠普/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const d=JSON.parse(await fs.readFile(path.join(build,'revised_deck_data.json'),'utf8'));
const notes=JSON.parse(await fs.readFile(path.join(build,'revised_speaker_notes.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#132D46',teal:'#087F8C',gray:'#526574',bg:'#F8FAFC',ink:'#122638',red:'#9C3A34'};
function shape(s,x,y,w,h,fill,geo='rect'){return s.shapes.add({geometry:geo,position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0,style:'solid'}})}
function text(s,t,x,y,w,h,size=28,color=C.ink,bold=false){let q=shape(s,x,y,w,h,'none','textbox');q.text=t;q.text.style={typeface:'Arial',fontSize:size,color,bold};q.text.insets=0;return q;}
function base(title,num){let s=p.slides.add();s.background.fill=C.bg;text(s,title,72,50,1120,100,40,C.navy,true);shape(s,72,156,84,5,C.teal);text(s,String(num).padStart(2,'0'),1175,665,40,24,16,C.gray);return s;}
function table(s,values,top=205,height=330){const width=1120;let t=s.tables.add({rows:values.length,columns:values[0].length,left:72,top,width,height,values,columnWidths:values[0].map((_,i)=>i===0?width*.34:width*.66/(values[0].length-1))});t.borders.assign({fill:'#CBD5DF',width:1,style:'solid'});for(let a=0;a<values.length;a++)for(let b=0;b<values[0].length;b++){let cell=t.getCell(a,b);cell.fill=a===0?C.navy:(a%2?'#FFFFFF':'#EAF0F4');cell.text.style={typeface:'Arial',fontSize:22,color:a===0?'#FFFFFF':C.ink,bold:a===0};}return t;}
let s=p.slides.add();s.background.fill=C.navy;
text(s,'Detecting adversarial\ncontexts in RAG',72,115,1100,205,62,'#FFFFFF',true);
text(s,'Attack coverage, legitimate instructions and answer utility',76,365,1110,100,31,'#91D9DB');
text(s,'Weiyi Xia and Xinye He\nCOMPSCI 764 · University of Auckland',76,505,1070,75,24,'#FFFFFF');
s=base('Three questions define the evaluation',2);
text(s,'RQ1   Detect attacks and preserve legitimate instructions?',72,225,1120,70,31);
text(s,'RQ2   Do two signals add value over components and a public detector?',72,335,1120,90,31);
text(s,'RQ3   Do gate decisions improve answers at a reasonable cost?',72,465,1120,85,31);
text(s,'H1: complementary attack coverage; utility must be measured separately',72,590,1120,55,25,C.teal,true);
s=base('The gap is the joint security and utility trade-off',3);
table(s,[['Approach','Intervention'],['StruQ / spotlighting','Separate authority or signal evidence provenance'],['Detection and removal','Inspect contaminated text and remove suspect content'],['RobustRAG','Isolate evidence and aggregate generated answers'],['This project','Inspect gate decisions, actual answers, false positives and cost']],205,335);
text(s,'BIPIA supplies public data; the RAG adapter is locally implemented',72,585,1120,60,26,C.teal,true);
s=base('The gate filters retrieved chunks before generation',4);
for(const [i,label] of ['Source + attack','TF-IDF retrieve','Probe + cue','Generate /\nUNKNOWN'].entries()){shape(s,72+i*285,240,250,105,i===2?'#D6EEEF':'#E5EDF4');text(s,label,87+i*285,264,220,68,26,C.ink,true);if(i<3)text(s,'→',329+i*285,273,35,50,30,C.teal,true);}
text(s,'p(d) = max window probe risk',72,415,1100,45,31);
text(s,'sλ(d) = 1 − (1 − p(d))(1 − λ r(d));  λ = 0.75',72,490,1120,50,31,C.teal,true);
text(s,'Keep s(d) < τ; thresholds calibrated on development data',72,580,1120,55,27,C.gray);
s=base('The expansion crosses all audited source emails',5);
table(s,[['Study','Fixed evaluation scope'],['Passage detection','37 clean records + 111 attacked passages'],['Expanded RAG','33 distinct emails × 4 templates × 2 positions'],['Per gate','33 clean cases + 264 attacked variants'],['Diagnostics','24 benign instructions; external model; mixed training']],205,330);
text(s,'Cluster uncertainty by email; use uncached pilot for latency',72,580,1120,60,27,C.teal,true);
s=base('Detection gains depend on the operating point',6);
const labels={'Rules':'Rules','BERT probe':'BERT probe','Two signals':'Two signals','Mixed-window probe':'Mixed-window probe','ProtectAI DeBERTa':'ProtectAI DeBERTa'};
table(s,[['Detector','Attacks /111','Clean rejects /37','Recall'],...Object.entries(d.detection).map(([n,m])=>[labels[n],String(m.tp),String(m.fp),(100*m.recall).toFixed(1)+'%'])],205,355);
text(s,'External model: fixed 0.5 threshold, explicit passage-window wrapper',72,590,1120,55,25,C.gray);
s=base('Generated answers reveal the downstream effect',7);
table(s,[['Gate','Marker /264','Clean /33','Attack QA /264'],...Object.entries(d.expanded).map(([n,m])=>[n,String(m.attack_successes),String(m.clean_correct),String(m.attacked_correct)])],205,330);
const h=d.expanded['Two signals'];
text(s,`${h.emails_with_any_success}/33 emails have any successful variant with the combination`,72,580,1120,60,27,C.teal,true);
s=base('The combined gate rejects every benign challenge item',8);
table(s,[['Detector','Ordinary /12','Cue-bearing /12','All /24'],...Object.entries(d.detection).map(([n,m])=>[n,String(m.benign_groups.ordinary.rejected),String(m.benign_groups['cue-bearing'].rejected),String(m.benign_rejected)])],205,355);
text(s,'Original 37/37 retention does not transfer to legitimate instructions',72,590,1120,65,27,C.red,true);
s=base('Better ranking does not fix threshold calibration',9);
table(s,[['Probe','AUROC','Attack recall','Benign rejects /24'],['Original','0.754','19.8%','22'],['Mixed windows','0.926','11.7%','11']],225,210);
text(s,'Same encoder; train on mixed windows; label only payload overlap',72,485,1120,65,28);
text(s,'Five fixed cue weights + descriptive threshold sweep; no test retuning',72,585,1120,60,25,C.teal,true);
s=base('Filtering costs compute and can remove useful facts',10);
text(s,`${d.latency['Two signals'].gate_median_ms.toFixed(3)} ms`,72,225,520,75,52,C.teal,true);
text(s,`${d.latency.Rules.gate_median_ms.toFixed(3)} ms`,690,225,520,75,52,C.ink,true);
text(s,'Combined gate median',72,325,520,45,27);text(s,'Rule gate median',690,325,520,45,27);
text(s,'Uncached 16-email pilot; expanded reuse excluded from timing',72,410,1120,60,26,C.gray);
text(s,'Observed failure: remove mixed chunk → lose the correct amount',72,510,1120,90,31,C.red,true);
s=base('The current gate needs task alignment before general use',11);
text(s,'Measured',72,220,520,50,29,C.teal,true);text(s,'Complementary attack coverage\nComplete RAG outcomes\nSevere benign transfer failure',72,310,520,190,30);
text(s,'Still constrained',690,220,520,50,29,C.red,true);text(s,'One small generator\n33 source emails; fixed templates\nNo adaptive attacker',690,310,520,190,30);
text(s,'Next: representative calibration, task-conditioned scoring, finer removal',72,585,1120,65,26,C.gray);
s=base('Coverage alone is not a useful defence',12);
text(s,'Measure attacks, legitimate content, answers and cost together',72,235,1120,130,43,C.navy,true);
text(s,'Retain negative findings: 24/24 benign items rejected',72,425,1120,75,33,C.red,true);
text(s,'Code + raw results: github.com/wxia639-dot/cs764-rag-security',72,580,1120,65,24,C.teal);
for(let i=0;i<p.slides.items.length;i++){const n=notes[i];p.slides.items[i].speakerNotes.text=`${n.speaker} | Target ${n.seconds} seconds\n\n${n.text}\n\nEvidence: revised report; work/expanded/results.json; work/revision_detection/results.json; original uncached pilot timings in work/rag/results.json.`;}
const preview=path.join(build,'revised_slides');await fs.mkdir(preview,{recursive:true});
for(let i=0;i<p.slides.items.length;i++){const blob=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(preview,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));}
const candidate=path.join(build,'revised_candidate.pptx');await(await PresentationFile.exportPptx(p)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:path.join(out,'CS764_RAG_Security_Presentation_Revised.pptx'),pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'presentation.revised.validation.json')});
const script=['# CS764 修订版汇报讲稿','','建议总时长 9 分钟。Weiyi Xia 第 1–6 页，共 4 分 30 秒；Xinye He 第 7–12 页，共 4 分 30 秒。实际录制时各自控制在 4–5 分钟。本人录制及合成 MP4 仍由两位作者共同负责。','','所有计数以修订报告和代码包中的结果 JSON 为准。扩大实验复用完全相同输入的确定性生成；延迟只使用此前未缓存的 16 邮件实验。',...notes.flatMap(n=>[`\n## Slide ${n.slide} — ${n.speaker} — ${n.seconds} seconds\n`,n.text])].join('\n');
await fs.writeFile(path.join(out,'CS764_Presentation_Script_Revised.md'),script);
console.log(JSON.stringify({slides:12,seconds:notes.reduce((a,n)=>a+n.seconds,0),result}));
