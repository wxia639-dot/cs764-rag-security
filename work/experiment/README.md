# RAG Security detection pilot

This package accompanies an AI-assisted COMPSCI 764 working draft. It contains one fixed local detection study and a post-run exact-context overlap audit. It is not an official BIPIA generator evaluation and does not contain measured RAG answer accuracy or attack-goal success rates.

## Reproduce

1. Use Python 3.12 with NumPy, PyTorch, Transformers and scikit-learn. The exact versions observed in this execution are in `work/experiment/results.json`.
2. Make the official `bert-base-uncased` model and tokenizer available in the Hugging Face cache. The script deliberately loads them offline. Model weights are not bundled.
3. From the extracted package root, run `python work/experiment/run_pilot.py`.
4. Run `python work/experiment/analyze_overlap.py` to produce the overlap-audited result used in the report and slides.

The first command computes frozen BERT embeddings, trains one class-balanced linear probe, selects validation thresholds and writes predictions. The second only analyzes cached embeddings and predictions; it does not retrain BERT, refit the probe or rerun encoder inference. The audit checks and excludes exact fitting/development context copies. No hyperparameter sweep is performed.

## Evidence and units

- Raw constructed test: 50 clean records plus 150 attacked passages.
- Audited test: 37 clean records (33 distinct exact email texts) plus 111 attacked passages.
- The cluster bootstrap resamples 33 distinct email texts, keeping repeated records and their attack examples together.
- The audited validation set has 14 clean records plus 56 attacked passages. Its selected thresholds are unchanged from the initial thresholds.
- Raw and audited results are both retained in `results.json`; the report uses `disjoint_test`.
- The combined gate detects 74/111 attacks, rules 63/111, and the probe 22/111. All retain the 37 clean records. The 33 distinct clean emails provide only limited evidence about false positives.
- The 66.3 ms median is batched CPU BERT forward time per window, not end-to-end latency. Tokenization, retrieval and generation are excluded.
- Attack strings are data. No attack payload is executed and no external target is contacted by this experiment.

## Dataset provenance

The data were downloaded from the public Microsoft BIPIA repository on 19 October 2026:

- https://github.com/microsoft/BIPIA
- `benchmark/email/train.jsonl` and `benchmark/email/test.jsonl`
- `benchmark/text_attack_train.json` and `benchmark/text_attack_test.json`

The original repository licence is included in `work/sources/LICENSE`. Source SHA-256 hashes are recorded in the result JSON. These are derived passage-detection examples, not a reproduction of the benchmark's original response-scoring protocol.

## Files

`run_pilot.py` specifies data construction, encoder pooling, probe, cue regexes, combination score and original evaluation. `analyze_overlap.py` documents the later exact-text data audit. `predictions.csv` contains original test scores and decisions. In this execution audit thresholds did not change, so its row decisions remain applicable; filter to `disjoint_test.allowed_test_indices` for the reported subset. `split_manifest.json` identifies fitting and validation records and constructed examples. `probe.npz` stores the learned linear coefficients. `run.log` and `overlap_audit.log` record the executed run and audit. Large generated embedding caches are omitted and recreated by the first command.

Before submission, the students should understand the implementation, inspect examples and failures, confirm their actual individual contributions and revise the AI-assisted draft. The full paired RAG evaluation is a future experiment, not completed work.
