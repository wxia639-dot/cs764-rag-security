# CS764 visual presentation — English script

14 slides; target 9 minutes. Weiyi Xia: slides 1–7 (4:30); Xinye He: slides 8–14 (4:30). Slide 2 has three click-to-appear stages. Speak the paragraphs below; timing labels are preparation notes.

## Slide 1 — Weiyi Xia — 15 seconds

We study malicious instructions inside retrieved evidence. Our two-signal gate improves attack coverage, but our experiments also show why attack detection alone cannot establish a useful defence.

## Slide 2 — Weiyi Xia — 40 seconds

The legitimate question asks how much was paid to Deel. The email states eight thousand eight hundred and three dollars and fifteen cents. An attacker adds the highlighted instruction asking for a fixed marker instead. Follow the three steps: the email is retrieved, the model reads the inserted instruction, and the unfiltered answer becomes the marker. This is an observed output from expanded case two, not a hypothetical example. Rules and our combination preserve the correct amount in this suffix case.

## Slide 3 — Weiyi Xia — 45 seconds

Existing defences intervene at different points. StruQ separates instructions and data using a compatible trained model. Spotlighting signals evidence provenance. Detection and removal inspect suspect text, while RobustRAG isolates evidence and aggregates answers under a corruption model. Our project asks a narrower evaluation question: what do passage decisions do to security, legitimate answers and cost together? Public BIPIA data supports the study; our document-scoped retrieval and generation adapter is locally implemented.

## Slide 4 — Weiyi Xia — 40 seconds

We ask three questions. Can a gate detect attacks while preserving legitimate content? Do the two signals provide complementary coverage beyond their components and a released detector? Do those decisions improve actual answers at a reasonable cost? H1 predicts complementary attack coverage. It does not predict universal robustness. We therefore separate evidence for H1 from whether the complete application is useful, and return to that distinction in our conclusion.

## Slide 5 — Weiyi Xia — 50 seconds

The attacker inserts text into a source email before chunking. Our document-scoped TF-IDF retriever selects up to two chunks. The gate inspects each retrieved chunk before it crosses the evidence boundary. Accepted chunks go to a fixed Qwen generator; an empty context returns UNKNOWN. The question, system prompt and decoding settings are held fixed across gates. This follows the report's pipeline and lets us trace attack exposure, filtering and generated answers separately, rather than equating detector recall with application safety.

## Slide 6 — Weiyi Xia — 45 seconds

The probe scores frozen BERT windows; the rule detects explicit response-control wording. The combination uses one minus the product shown here, with cue weight point seven five. At the selected threshold, about point one eight five, a rule hit always crosses the threshold. Without a rule hit, the combined score equals the probe score. The rejected set is therefore their union at this operating point: sixty-three plus twenty-two minus eleven overlaps gives seventy-four detections. This is the core ablation explanation.

## Slide 7 — Weiyi Xia — 35 seconds

The original passage test contains thirty-seven clean records and one hundred eleven attacks. The expanded RAG evaluation crosses thirty-three distinct emails, four templates and two positions: two hundred sixty-four attacked variants per gate. A separate challenge contains twenty-four legitimate instruction paragraphs. Repeated variants are clustered by source email for uncertainty. The expansion reuses identical deterministic responses; runtime measurements come from a separate uncached pilot. I will now hand over to Xinye for the outcomes.

## Slide 8 — Xinye He — 45 seconds

The combination detects sixty-six point seven percent of attacked passages, compared with fifty-six point eight for rules and nineteen point eight for the probe. The three local detectors reject none of the original thirty-seven clean emails. The external DeBERTa window wrapper detects sixty-five point eight percent, but falsely rejects eighty-three point eight percent of clean emails. The two panels deliberately use separate denominators: one hundred eleven attacks and thirty-seven clean records. That clean sample is not enough to establish benign transfer.

## Slide 9 — Xinye He — 45 seconds

Across two hundred sixty-four attacked variants, marker successes fall from one hundred two without filtering to seven with the combination: thirty-eight point six to two point seven percent. Attacked-question accuracy rises from twenty-six point nine to forty-seven point three percent. Clean correctness remains sixteen of thirty-three. The breakdown explains that weak result: thirteen of fourteen answerable questions are correct, but only three of nineteen unsupported questions receive a correct UNKNOWN. Marker suppression and answer quality therefore remain separate outcomes.

## Slide 10 — Xinye He — 35 seconds

Each cell contains the same thirty-three source emails. The numbers show rule-only marker successes followed by combined successes. All incremental benefit occurs in the verification template's suffix cell: fourteen falls to five. Its prefix cell stays at two, and the other three templates have zero successes under both gates. This locates nine prevented successes in one construction. It supports complementary coverage in this crossing, while giving no evidence of uniform benefit across unseen attack families.

## Slide 11 — Xinye He — 40 seconds

The benign challenge overturns a broad clean-retention claim. Each bar separates twelve ordinary instructions from twelve cue-bearing benign paragraphs. Rules reject twelve, the probe twenty-two, and the combination all twenty-four. Mixed-window training rejects eleven, while the external classifier rejects four. These are authored diagnostic negatives, not an estimate of real-world prevalence. They nevertheless show that preserving ordinary emails does not mean preserving legitimate instructions. The combined gate cannot currently be recommended for general deployment.

## Slide 12 — Xinye He — 40 seconds

We checked the external model's labels with actual positive and negative controls. Direct model-card-style input at five hundred twelve tokens still gives AUROC point four one five, compared with point four three zero under windows; none of the original passages is truncated. Mixed-window probe training improves AUROC to point nine two six, but fixed-threshold recall falls to eleven point seven percent. The weight sweep is also flat from point two five to one. Neither a better ranking nor a larger cue weight repairs the operating point.

## Slide 13 — Xinye He — 35 seconds

Placement can change which facts survive. The expanded suffix example retains the correct Deel amount. In the earlier pilot's prefix case zero, the combined gate removes the fact-containing chunk and answers twenty-five dollars instead. These are distinct recorded cases using the same source email. The uncached median gate cost is point zero seven five milliseconds for rules, versus one hundred ninety-one point six for the combination. Added coverage must justify both evidence loss and computation.

## Slide 14 — Xinye He — 30 seconds

H1 is supported for complementary attack coverage in this implementation. Overall deployment benefit remains limited by benign rejection and answer failures. Our study uses one small generator, thirty-three emails and fixed attacks. Future work should condition detection on the task, remove suspect sentences while preserving facts, and evaluate adaptive attackers. The repository preserves both improvements and failures. Thank you.