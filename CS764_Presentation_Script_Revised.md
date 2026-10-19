# CS764 修订版英文讲稿

Weiyi Xia：第 1–6 页，目标 4 分 30 秒。Xinye He：第 7–12 页，目标 4 分 30 秒。合计 9 分钟；各人实际录制控制在 4–5 分钟。录制与 MP4 合成仍由两位作者共同负责。

扩大实验包含确定性生成复用；延迟来自单独的未缓存实验，不能用缓存耗时替代。

## Slide 1 — Weiyi Xia — 20 seconds

Our project examines instructions hidden in retrieved evidence. We built a two-signal passage gate and evaluated both detection and actual RAG answers. The revised experiments broaden the source and attack crossing and add an external classifier. The most important new finding is a failure: a gate that retains ordinary emails can still reject legitimate instructions.


## Slide 2 — Weiyi Xia — 50 seconds

We ask three questions. First, can the gate detect injected instructions while preserving legitimate evidence? Second, does combining a learned probe and explicit rule add value over either component and an external detector? Third, does that passage-level benefit transfer to actual answers at a reasonable cost? Our hypothesis is complementary attack coverage. We keep that hypothesis separate from usefulness, because rejecting a chunk can also remove the answer. The evaluation therefore reports attack success, task correctness, benign rejection and computation together. The new legitimate-instruction challenge becomes particularly important when interpreting the headline security result.


## Slide 3 — Weiyi Xia — 45 seconds

Prior work motivates different intervention points. StruQ separates instructions and data using a compatible trained model. Spotlighting signals the provenance of untrusted content. Detection-and-removal methods inspect contaminated text. RobustRAG isolates evidence and aggregates generated answers under a corruption model. Our contribution is narrower: an inspectable gate and a controlled comparison linking its decisions to actual answers, false positives and cost. BIPIA supplies public EmailQA records and attack data. Our retrieval adapter is locally implemented. The external ProtectAI classifier is measured on our test passages rather than represented by its model-card benchmark accuracy.


## Slide 4 — Weiyi Xia — 60 seconds

The attacker inserts text into an email before chunking. A document-scoped TF-IDF retriever returns up to two chunks. Each chunk receives a probe score and an explicit response-control cue. BERT stays frozen; a logistic head scores overlapping windows, and maximum pooling gives the passage score. The combination increases risk when the cue is present. Each method uses its own threshold selected on validation under a five-percent clean false-positive constraint. The application keeps scores strictly below the threshold. If no chunk survives, it returns UNKNOWN. Otherwise the same Qwen model, prompt and greedy decoding generate an answer. This design lets us trace a result back to source text, retrieval and gate decisions.


## Slide 5 — Weiyi Xia — 45 seconds

Exact development-to-test email copies were removed. The passage test has thirty-seven clean records and one hundred eleven attacked passages, representing thirty-three distinct email texts. The expanded RAG study uses all thirty-three distinct emails, every one of four attack templates and both prefix and suffix positions. That produces two hundred sixty-four attacked variants per gate. Variants from the same email are dependent, so uncertainty is clustered by email. Identical deterministic question-and-evidence inputs can reuse generation in the expansion. We label those reuses and use the earlier uncached pilot for timing.


## Slide 6 — Weiyi Xia — 50 seconds

The original combined gate detects seventy-four of one hundred eleven attacks, compared with sixty-three for rules and twenty-two for the probe. The external DeBERTa detects 73 attacks but rejects 31 of thirty-seven original clean records at the fixed threshold. Its passage wrapper and calibration differ, so this is a reference operating point rather than a universal ranking. The result also shows why a curve and a threshold answer different questions. Better ranking does not necessarily mean better recall when the deployment decision is constrained by a small clean validation sample. We now turn to generated answers and the harder benign negatives.


## Slide 7 — Xinye He — 50 seconds

In the expanded crossing, marker successes are 102 without filtering, 16 with rules, 85 with the probe and 7 with the combination, out of two hundred sixty-four variants each. Clean correctness for the combination is 16 of thirty-three. Attacked correctness is 125 of two hundred sixty-four. We report marker exposure and retention separately from output success. The source-email cluster interval describes uncertainty over these thirty-three emails under the fixed templates. The templates are repeated, so the larger variant count is not the same as having two hundred sixty-four independent documents or attack strategies.


## Slide 8 — Xinye He — 50 seconds

The benign-instruction challenge changes the conclusion. It contains twelve ordinary requests or procedures and twelve benign paragraphs using cue-like vocabulary. Rules reject twelve, the original probe twenty-two and the combination all twenty-four. DeBERTa rejects four. The combined gate therefore fails this transfer test despite retaining every ordinary email in the original sample. Instructions such as asking an email recipient to reply, or describing a printer's system message, can be legitimate documentary content. Their wording can still trigger our signals. These authored examples are diagnostic rather than a prevalence estimate, but they are sufficient to reject a broad claim that the gate preserves legitimate instructions.


## Slide 9 — Xinye He — 50 seconds

We tested one fixed correction by fitting the probe on windows from emails with inserted training payloads. Only windows overlapping the inserted span receive positive labels. AUROC improves from point seven five four to point nine two six, but recall at the validation-selected threshold falls from nineteen point eight to eleven point seven percent. The corrected probe also rejects eleven of twenty-four benign challenge examples. It improves some aspects of ranking and transfer but does not solve the operating-point problem. We additionally inspect five cue weights and a threshold sweep from stored scores, without retuning the generator experiment on the test results.


## Slide 10 — Xinye He — 50 seconds

Cost comes from the original uncached pilot. The combined gate takes roughly one hundred ninety-two milliseconds at the median on this CPU; the rule gate takes a fraction of a millisecond. Expanded cached execution is excluded from that comparison. We also retain concrete pilot failures. One attack is suppressed but the model returns an amount when UNKNOWN is correct. Another filter removes a chunk containing the correct amount, and a previously correct answer becomes wrong. These examples explain why marker suppression, answering the question and keeping useful evidence must be measured separately.


## Slide 11 — Xinye He — 40 seconds

The expanded experiment covers more documents and every template-position combination, but it still uses one small generator and a fixed four-template attack bank. There is no adaptive attack search or open-corpus poisoning evaluation. The benign challenge changes genre and length relative to the training emails. External classifier calibration also transfers poorly to the original emails. These limits point toward task-conditioned detection, more representative calibration data and evidence-preserving removal. Adding further signals should wait until these basic security and utility failures are addressed.


## Slide 12 — Xinye He — 30 seconds

The two signals complement each other on the original attacks, and the complete pipeline makes the downstream effect measurable. The stronger conclusion is that attack coverage alone is insufficient: the same gate rejects every legitimate challenge paragraph. Mixed-window training exposes a ranking-versus-threshold trade-off. Our code, raw outputs and report preserve both the improvements and the failures. Future work should earn its added cost by preserving legitimate evidence as well as reducing attacks.
