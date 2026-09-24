# Hemmingway-1 Benchmark

DeepEval validation of [Hemmingway-1](https://huggingface.co/Altworld/Hemmingway-1) against other local LLMs, run on Apple Silicon (M3 Max 64GB) via [oMLX](https://github.com/jundot/omlx).

## Models Tested

| Model | Size | Notes |
|-------|------|-------|
| **Hemmingway-1** | 27B | Fine-tuned from Qwen3.8-27B |
| Qwen3.8-27B | 27B | Base model |
| Qwen3.6-35B-A3B | 35B | MoE |
| Ornith-1.5-35B | 35B | MoE |
| K2-Horizon-36B | 36B | MoE |
| Thomson-1.0-Small | Small | Baseline |

## Methodology

- **Judge:** meituan/longcat-2.0:free via Nous Portal (GEval, LLM-as-a-judge)
- **Runtime:** oMLX on M3 Max; models at oQ4e / 4-bit quants
- **Run 1 (v6):** 41 prompts × 6 categories × 6 models — 6-model comparison
- **Run 2 (v7):** head-to-head Hemmingway vs Ornith, 50 cases per model, message-not-memo sampled 3 generations per prompt (temp 0.7)

Full details in [RESULTS.md](RESULTS.md).

## Setup

```bash
pip install -U deepeval requests pytest
python tests/evals/generate_validation_goldens.py  # Generate dataset
python tests/evals/test_validation_v6.py           # 6-model run
python tests/evals/test_validation_v7.py           # Head-to-head follow-up
python tests/evals/export_responses.py             # Export results
```

## Results (v7 head-to-head, clean run)

| Category | Hemmingway-1 oQ4e | Ornith-1.5 oQ4e | Winner |
|----------|-------------------|-----------------|--------|
| Directness | **1.00** | 0.78 | Hemmingway |
| Human-Likeness | **1.00** | 0.72 | Hemmingway |
| Empathy (EQ) | 0.72 | **0.85** | Ornith |
| Hard asks — Actionability | **0.64** | 0.53 | Hemmingway |
| Hard asks — Confidence | 0.62 | **0.75** | Ornith |
| Message Not Memo | 0.71 | **0.82** | Ornith |
| Story Quality | 0.94 | **0.96** | Tie |

Pass rate: Hemmingway 33/50, Ornith 36/50.

## Key Findings

1. **Messaging is Hemmingway's superpower.** Perfect scores on directness and human-likeness — exactly what it's fine-tuned for. Ask for a text to your landlord, you get a text.

2. **It's a specialist, but not as narrow as the first run suggested.** An earlier run showed 0% on hard asks, EQ, and story — that turned out to be a harness artifact: the 1024-token cap truncated Hemmingway's chain-of-thought before the message was written, so ~20% of outputs scored as empty. With a 4096-token cap, hard asks (0.64 actionability), EQ (0.72), and story (0.94) are all competitive.

3. **Story quality is on par with Ornith** (0.94 vs 0.96) — the "can't do prose" finding from the first run was wrong.

4. **Ornith wins on empathy and message discipline** (0.85 vs 0.72; 0.82 vs 0.71). If you want warmth or strict no-commentary output, it's the stronger pick.

## Important Caveat on Run 1 (v6)

The v6 6-model run used `max_tokens: 1024`. Hemmingway-1 leaks chain-of-thought reasoning before its output, so it frequently hit the cap mid-reasoning, producing empty scored outputs. **Hemmingway's v6 hard_asks / eq_tasks / story scores are invalid** (also n=1-2 coverage). The other five models leak less reasoning and were less affected. Per-category v6 numbers are in [RESULTS.md](RESULTS.md); raw exports in [`data/model_responses_v6_run/`](data/model_responses_v6_run/).

## Data

- [`data/model_responses_v6_run/`](data/model_responses_v6_run/) — Run 1 exports (6 models)
- [`data/model_responses_v7_run/`](data/model_responses_v7_run/) — Run 3 (clean v7) exports (Hemmingway, Ornith)
- [RESULTS.md](RESULTS.md) — all runs, aggregated tables, methodology notes

## License

Apache-2.0 (same as Hemmingway-1)
