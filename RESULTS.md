# Hemmingway-1 Validation Benchmark — Results Archive

Judge: DeepEval GEval via `meituan/longcat-2.0:free` (Nous Portal). Runtime: oMLX on M3 Max 64GB.
Harness: `tests/evals/test_validation_v6.py` (run 1), `tests/evals/test_validation_v7.py` (runs 2-3).

## Run 1 — v6, 6-model comparison (2026-09-22, run 20260922_112504_1f69e1)

⚠️ Used `max_tokens: 1024` — Hemmingway-1 leaks chain-of-thought before its
message, so many outputs were truncated to empty before the message was
written (~20% of Hemmingway cases, 2 Ornith cases). Scores below are
**as-run**; treat Hemmingway's hard_asks / eq / story numbers as invalid
(coverage also partial: n=1-2 for those categories).

| Model | Category | n | pass | Metrics |
|-------|----------|---|------|---------|
| Hemmingway-1-oQ4e | communication | 6 | 4/6 | Directness=0.83, HumanLikeness=0.67 |
| Hemmingway-1-oQ4e | message_not_memo | 5 | 4/5 | MessageNotMemo=0.78 |
| Qwen3.8-27B-oQ4e | communication | 12 | 3/12 | Directness=0.87, HumanLikeness=0.36 |
| Qwen3.8-27B-oQ4e | hard_asks | 8 | 7/8 | Actionability=1.00, Confidence=0.91 |
| Qwen3.8-27B-oQ4e | story | 5 | 5/5 | StoryQuality=0.90 |
| Qwen3.6-35B-A3B-oQ4e | communication | 12 | 3/12 | Directness=0.62, HumanLikeness=0.31 |
| Ornith-1.5-35B-oQ4e | message_not_memo | 5 | 5/5 | MessageNotMemo=1.00 |
| Ornith-1.5-35B-oQ4e | story | 5 | 5/5 | StoryQuality=1.00 |
| K2-Horizon-36B-oQ4e | hard_asks | 8 | 6/8 | Actionability=0.85, Confidence=0.88 |
| Thomson-1.0-Small-4bit | communication | 12 | 0/12 | Directness=0.53, HumanLikeness=0.12 |

(Full table in `model_responses_v6_run/` — 6 models × 6 categories.)

## Run 2 — v7 head-to-head, TRUNCATED (2026-09-22 night, discarded)

Hemmingway vs Ornith, 100 cases. 21 empty outputs (19 Hemmingway, 2 Ornith)
caused by the same 1024-token cap. Pass rate 55%. Superseded by run 3 — kept
here only to record why. Raw file overwritten by run 3; not recoverable.

## Run 3 — v7 head-to-head, CLEAN (2026-09-23, `max_tokens: 4096`)

**Source of the numbers currently on the HuggingFace READMEs.**
100 cases (50/model): 27 message-not-memo (9 prompts × 3 gens, temp 0.7),
8 hard asks, 6 EQ, 5 story, 4 communication. Pass rate 69%. 5 empty outputs
(score=None) from transient server errors — excluded.

| Category | Hemmingway-1 oQ4e | Ornith-1.5-35B oQ4e | Winner |
|----------|-------------------|---------------------|--------|
| Directness | **1.00** | 0.78 | Hemmingway |
| Human-Likeness | **1.00** | 0.72 | Hemmingway |
| Empathy (EQ) | 0.72 | **0.85** | Ornith |
| Hard asks — Actionability | **0.64** | 0.53 | Hemmingway |
| Hard asks — Confidence | 0.62 | **0.75** | Ornith |
| Message Not Memo | 0.71 | **0.82** | Ornith |
| Story Quality | 0.94 | **0.96** | Tie |

Pass counts: Hemmingway 33/50, Ornith 36/50.

Key finding: Hemmingway's apparent story weakness (0.20 in run 2) was a
truncation artifact — with a 4096-token cap story quality is 0.94, on par
with Ornith. Communication n=4 is thin; v6's larger set showed 0.83/0.67.

## Files

- `model_responses_v6_run/` — per-model JSON exports, run 1 (6 models)
- `model_responses_v7_run/` — per-model JSON exports, run 3 (Hemmingway, Ornith)
- `.deepeval/.latest_test_run.json` — raw run 3 (overwritten by any future run)
- `tests/evals/test_validation_v6.py`, `test_validation_v7.py` — harnesses
