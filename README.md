# CS764 RAG Security

Passage filtering in a document-scoped RAG application. This repository contains the complete reproducibility archive, revised report and presentation. The source archive preserves `work/` directories so the scripts run with their documented paths.

## Contents

- `CS764_Code_and_Results_Revised.zip`: source, public source data and licence, fitted coefficients, all raw outputs, fixed settings, summaries, figures and report/slide authoring sources.
- `CS764_RAG_Security_Report_Revised.pdf`: IEEEtran conference-format report.
- `CS764_RAG_Security_Presentation_Revised.pptx`: editable 12-slide presentation with notes.
- `CS764_IEEE_LaTeX_Source.zip`: editable IEEEtran project and vector figures.

## Findings and limits

The original combination detects 74/111 attacked passages and rejects 0/37 unmodified email records. It rejects **24/24** authored legitimate instruction paragraphs. This is a concrete benign-transfer failure, so the current gate is not recommended for general deployment.

The expanded study uses 33 distinct emails, four fixed marker templates and two positions: 264 attacked variants per gate and 1,188 total decisions. Unfiltered marker successes: 102/264; combined: 7/264. Clean combined correctness: 16/33. Variants are clustered by source email for uncertainty. The expansion reuses exact deterministic question/evidence responses; all reuse origins are logged. Latency uses the separate uncached 16-email pilot.

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
