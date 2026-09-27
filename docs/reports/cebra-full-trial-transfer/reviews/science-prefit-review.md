No findings.

APPROVE — no must-fix scientific/logic issues found in the prefit protocol.

Evidence verified:
- Leakage gate: protocol forbids validation navigation arrays/counts/model inputs at `docs/reports/cebra-full-trial-transfer/protocol.md:38-47`.
- Full-trial terminology is disclosed as cue first-second plus complete 100 ms nav bins, excluding tails at `protocol.md:55-61`.
- Pseudopopulation limits are explicit at `protocol.md:25-29,81-88` and consistent with `docs/analysis-contract.md:25-43,92-97`.
- Pair-bank Time semantics avoid cross-row positives at `protocol.md:71-88`.
- Phase-balanced full training and matched scaler/update/seed/decoder are specified at `protocol.md:92-116`.
- Null estimand and exposed-validation limitations are stated at `protocol.md:136-145`.
- No “Time label-free assembly” claim found.

Residual risks:
- Code implementation was not reviewed here.
- Budget feasibility still depends on the required synthetic runtime check before biological fitting.