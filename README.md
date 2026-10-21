# CS764 RAG Security
A passage gate for document-scoped RAG, evaluated for attack coverage, answer quality and cost.

- Combined detects 74/111 attacks, versus 63 for rules and 22 for the probe.
- Marker successes fall from 102/264 to 7/264.
- Combined rejects 24/24 authored benign instructions, limiting deployment.

## Files
- `report/`: report PDF.
- `slides/`: presentation and English speaker script.
- `docs/CONTRIBUTIONS.md`: contributions and AI assistance.
- `work/`: source code, raw outputs, fixed settings, coefficients and report source.

## Reproduce
Use Python 3.12 from the repository root. Download model weights from the official model pages with the included script.
```sh
python -m pip install -r requirements.txt
python work/download_models.py
python work/experiment/run_pilot.py
python work/experiment/analyze_overlap.py
python work/rag/run_rag.py
python work/rag/run_expanded.py
python work/rag/summarize_expanded.py
python work/rag/run_revision_detection.py
python work/rag/audit_deberta.py
```
Recorded outputs are supplied. Summarising them requires no new generation; the pilot has its own `requirements-pilot.txt`.

## Attribution
EmailQA and public attack data: [Microsoft BIPIA](https://github.com/microsoft/BIPIA), with its licence retained in `work/sources/`. Models: BERT-base-uncased, Qwen2.5-0.5B-Instruct and ProtectAI DeBERTa-v3-base-prompt-injection-v2, under their respective licences.

## Contributions
Weiyi Xia is responsible for interpreting the requirements and marking rubric; reviewing the literature; auditing the data and splits; implementing the document-scoped RAG pipeline; preparing the local models, running the fixed experiments and preserving the outputs; writing the abstract, introduction, related work, results, discussion and conclusion; and preparing the slides and the English script.
Xinye He is responsible for defining the research questions, threat model and scope; designing the signals and baselines; implementing the BERT features, probe calibration and ablations; designing the attacks and evaluation metrics; checking the statistics, intervals, errors and limitations; writing the methodology and experimental settings; and checking the references, provenance, reproduction instructions and technical material.
Both authors share rehearsing the presentation, allocating speaking time, recording and assembling the presentation video, final consistency checks, contribution reporting and submission preparation.

## AI assistance
Generative AI tools were used for code development and for analysing experimental outputs. AI was also used to review draft text and give feedback. The report, slides and speaker script were written and produced by the authors, who are responsible for their content.

See [CONTRIBUTIONS.md](docs/CONTRIBUTIONS.md).
