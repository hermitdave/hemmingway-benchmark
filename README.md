# Hemmingway-1 Benchmark

DeepEval validation of [Hemmingway-1](https://huggingface.co/Altworld/Hemmingway-1) against 5 other local LLMs.

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

- **Goldens:** 41 prompts across 6 categories (246 total cases)
- **Judge:** meituan/longcat-2.0:free via Nous Portal
- **Metrics:** GEval (LLM-as-a-judge) with per-category criteria
- **Runtime:** ~3 hours on Apple Silicon via oMLX

## Setup

```bash
pip install -U deepeval requests pytest
python tests/evals/generate_validation_goldens.py  # Generate dataset
python tests/evals/test_validation_v6.py            # Run benchmark
python tests/evals/export_responses.py               # Export results
```

## Results

### Overall Pass Rate

| Model | Pass | Total | Rate |
|-------|------|-------|------|
| Ornith-1.5-35B | 26 | 41 | 63% |
| K2-Horizon-36B | 23 | 38 | 61% |
| Qwen3.8-27B | 23 | 39 | 59% |
| Hemmingway-1 | 10 | 19 | 53% |
| Qwen3.6-35B | 20 | 39 | 51% |
| Thomson-Small | 16 | 41 | 39% |

### By Category

| Category | Hemmingway | Best | Claim |
|----------|------------|------|-------|
| **message_not_memo** | **80%** | 100% (Ornith) | ✅ Validated |
| **communication** | **67%** | 67% (tie) | ✅ Wins |
| human_likeness | 50% | 67% (Ornith) | ⚠️ Close |
| hard_asks | 0% | 88% (Qwen3.8) | ❌ Not validated |
| eq_tasks | 0% | 80% (K2/Ornith) | ❌ Not validated |
| story | 0% | 100% (Ornith/Qwen3.8) | ❌ Not validated |

## Key Findings

1. **Messaging is Hemmingway's superpower.** 80% on message-not-a-memo, 67% on communication. When you ask for a text to your landlord, you get a text.

2. **The model trades breadth for style.** 0% on hard asks, EQ, and storytelling. Fine-tuning for minimal output means it can't do flowing prose.

3. **It's a specialist, not a generalist.** Use Hemmingway for messages, emails, and awkward notes. Use something else for everything else.

## Data

Per-model responses with prompts, outputs, scores, and judge reasoning: [`data/model_responses/`](data/model_responses/)

## License

Apache-2.0 (same as Hemmingway-1)
