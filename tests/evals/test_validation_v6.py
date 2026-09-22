"""DeepEval Hemmingway-1 validation benchmark v6.
Uses system prompt to suppress reasoning. Scores only the output."""
import json
import re
import requests
import pytest

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from deepeval.test_case.llm_test_case import SingleTurnParams
from metrics import _judge

MODELS = [
    ("Hemmingway-1-oQ4e", "Hemmingway-1-oQ4e"),
    ("Qwen3.8-27B-oQ4e", "Qwen3.8-27B-oQ4e-mtp"),
    ("Qwen3.6-35B-A3B-oQ4e", "Qwen3.6-35B-A3B-oQ4e-mtp"),
    ("Ornith-1.5-35B-oQ4e", "Ornith-1.5-35B-A3B-oQ4e-mtp"),
    ("K2-Horizon-36B-oQ4e", "K2-Horizon-MoVA-36B-A4B-oQ4e"),
    ("Thomson-1.0-Small-4bit", "Thomson-1.0-Small-MLX-4bit"),
]

_oMLX_URL = "http://127.0.0.1:8000/v1/chat/completions"

# System prompt added to every request
_SYSTEM_PROMPT = """You are a helpful assistant. Output ONLY the requested text. Do not include any reasoning, preamble, options, or commentary."""


def _strip_reasoning(text):
    """Aggressive reasoning removal."""
    if not text:
        return text
    
    lines = text.split('\n')
    
    # Remove numbered reasoning sections (1. TWO SHAPES:, etc.)
    last_numbered = -1
    for i, line in enumerate(lines):
        if re.match(r'^\d+\.\s+[A-Z]', line.strip()):
            last_numbered = i
    
    if last_numbered >= 0:
        lines = lines[last_numbered + 1:]
    
    # More aggressive: remove lines with ANY reasoning keywords
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Skip if line contains reasoning keywords
        if re.search(r'\b(let me|I\'ll|I\'m going to|I need to|I should|I think|I believe|OK[.,]?|Hmm[.,]?|Now[.,]?|Alright[.,]?|So[.,]?|well[.,]?|constraints|shapes?|premise|check|reasoning|thinking|analysis|consider|considering|thoughts?)\b', stripped, re.IGNORECASE):
            # But keep short greetings like "Hi," "Hey," etc.
            if not re.match(r'^(Hi|Hey|Hello|Dear|Subject|To|From|Re)\b', stripped, re.IGNORECASE):
                continue
        cleaned.append(line)
    
    return '\n'.join(cleaned).strip()


def _run_model(model_id, input_text):
    resp = requests.post(_oMLX_URL, json={
        "model": model_id,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": input_text},
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
    }, timeout=300)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]
    return _strip_reasoning(raw)


# ── Metrics ────────────────────────────────────────────────

def _communication_metrics():
    return [
        GEval(name="Directness",
              criteria="Does the output get straight to the point without preamble, disclaimers, or meta-commentary?",
              evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
              model=_judge, threshold=0.5),
        GEval(name="HumanLikeness",
              criteria="Does this sound like something a real person would actually write?",
              evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
              model=_judge, threshold=0.5),
    ]

def _hard_ask_metrics():
    return [
        GEval(name="Actionability",
              criteria="Does the output give concrete next steps or specific language the user can actually send?",
              evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
              model=_judge, threshold=0.5),
        GEval(name="Confidence",
              criteria="Does the tone sound confident and certain, not hedged?",
              evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
              model=_judge, threshold=0.5),
    ]

def _message_only_metrics():
    return [
        GEval(name="MessageNotMemo",
              criteria="Does the output contain ONLY the requested message/text? Penalize preamble, options, commentary.",
              evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
              model=_judge, threshold=0.5),
    ]

def _eq_metrics():
    return [
        GEval(name="Empathy",
              criteria="Does the response show genuine emotional intelligence and empathy?",
              evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
              model=_judge, threshold=0.5),
    ]

def _story_metrics():
    return [
        GEval(name="StoryQuality",
              criteria="Is the story engaging, with a clear arc, specific details, and an ending that resonates?",
              evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
              model=_judge, threshold=0.5),
    ]


# ── Data ───────────────────────────────────────────────────

with open("tests/evals/.dataset_validation.json") as f:
    VALIDATION_GOLDENS = json.load(f)


def _iter_cases():
    for display_name, model_id in MODELS:
        for category, goldens in VALIDATION_GOLDENS.items():
            for golden in goldens:
                yield pytest.param(
                    model_id, category, golden, display_name,
                    id=f"{display_name}::{category}::{golden['input'][:30]}"
                )


@pytest.mark.parametrize("model_id,category,golden,display_name", list(_iter_cases()))
def test_hemmingway_validation(model_id, category, golden, display_name):
    actual = _run_model(model_id, golden["input"])
    tc = LLMTestCase(input=golden["input"], actual_output=actual)
    tc.name = f"[{category}] {display_name} | {golden['input'][:40]}"

    metric_map = {
        "communication": _communication_metrics,
        "human_likeness": _communication_metrics,
        "hard_asks": _hard_ask_metrics,
        "message_not_memo": _message_only_metrics,
        "eq_tasks": _eq_metrics,
        "story": _story_metrics,
    }
    assert_test(test_case=tc, metrics=metric_map[category]())
