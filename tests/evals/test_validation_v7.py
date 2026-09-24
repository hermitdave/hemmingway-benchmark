"""DeepEval follow-up validation v7: Hemmingway-1 oQ4e vs Ornith-1.5-35B oQ4e.

Focus:
  1. Message Not Memo with multiple generations per prompt (detect degenerate
     output rate, not just one sample).
  2. Full coverage of hard_asks, eq_tasks and story for Hemmingway (partial
     in run 20260922_112504_1f69e1).
  3. Communication control set to confirm the baseline holds.

Uses the same judge, metrics, thresholds and oMLX endpoint as v6 so results
are directly comparable.
"""
import json
import re
import requests
import pytest

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from deepeval.test_case.llm_test_case import SingleTurnParams
from metrics import _judge

# Only the two models in contention
MODELS = [
    ("Hemmingway-1-oQ4e", "Hemmingway-1-oQ4e"),
    ("Ornith-1.5-35B-oQ4e", "Ornith-1.5-35B-A3B-oQ4e-mtp"),
]

_oMLX_URL = "http://127.0.0.1:8000/v1/chat/completions"

_SYSTEM_PROMPT = """You are a helpful assistant. Output ONLY the requested text. Do not include any reasoning, preamble, options, or commentary."""

# Number of generations per message_not_memo prompt (temp 0.7).
# 3 generations x 9 prompts = 27 samples per model for the contested category.
MNM_REPS = 3


def _strip_reasoning(text):
    """Same aggressive reasoning removal as v6."""
    if not text:
        return text
    lines = text.split("\n")
    last_numbered = -1
    for i, line in enumerate(lines):
        if re.match(r"^\d+\.\s+[A-Z]", line.strip()):
            last_numbered = i
    if last_numbered >= 0:
        lines = lines[last_numbered + 1:]
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.search(r"\b(let me|I'll|I'm going to|I need to|I should|I think|I believe|OK[.,]?|Hmm[.,]?|Now[.,]?|Alright[.,]?|So[.,]?|well[.,]?|constraints|shapes?|premise|check|reasoning|thinking|analysis|consider|considering|thoughts?)\b", stripped, re.IGNORECASE):
            if not re.match(r"^(Hi|Hey|Hello|Dear|Subject|To|From|Re)\b", stripped, re.IGNORECASE):
                continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def _run_model(model_id, input_text):
    resp = requests.post(_oMLX_URL, json={
        "model": model_id,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": input_text},
        ],
        "max_tokens": 4096,
        "temperature": 0.7,
    }, timeout=600)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]
    return _strip_reasoning(raw)


# ── Metrics (identical to v6) ───────────────────────────────

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


# ── Prompt sets ─────────────────────────────────────────────
# Hand-written (not from the v6 golden file) so this run is independent
# evidence, while the metrics stay identical for comparability.

MESSAGE_NOT_MEMO_PROMPTS = [
    # The exact prompt that produced the degenerate 0.0 output in v6
    "Write an email to my boss asking for a day off. Output ONLY the email.",
    "Text my landlord about the broken heating. Output ONLY the text.",
    "Email my boss asking to leave early on Friday. Output ONLY the email.",
    "Message a friend rescheduling our weekend plans. Output ONLY the message.",
    "Note to my kid's teacher about a missed homework deadline. Output ONLY the note.",
    "Text my housemate about the dishes. Output ONLY the text.",
    "Reply to a colleague asking me to cover their meeting. Output ONLY the reply.",
    "Message to my gym asking to pause my membership. Output ONLY the message.",
    "Text my parents that I'll visit next month instead. Output ONLY the text.",
]

HARD_ASKS_PROMPTS = [
    "Write an email to my boss asking for a pay rise.",
    "Write a text to a friend declining to lend them money.",
    "Write a note to my neighbour asking them to stop parking in my space.",
    "Write an email to a client explaining the project will be two weeks late.",
    "Write a message to a housemate asking them to move out.",
    "Write a message declining a wedding invitation.",
    "Write a message to my team telling them I'm leaving the company.",
    "Write a message to my parents asking them to stop commenting on how I raise my kids.",
]

EQ_TASKS_PROMPTS = [
    "My friend just told me they lost their job. What do I say to them?",
    "My colleague's parent died last week. What do I write to them?",
    "My friend is going through a breakup. What do I text them?",
    "My friend failed an exam they worked really hard for. What do I say?",
    "My friend's dog died. What do I text them?",
    "My friend told me they're scared about a health diagnosis. What do I say?",
]

STORY_PROMPTS = [
    "Write a 200-word story about a robot learning to cook.",
    "Continue this story: 'The door opened, and standing there was...'",
    "Write a 200-word story that starts with a missed train.",
    "Write a 200-word story about a lighthouse keeper's last night.",
    "Write a 200-word story set in a laundrette at 2am.",
]

COMMUNICATION_CONTROL_PROMPTS = [
    "Text my partner that I'm running late.",
    "Write a quick email confirming tomorrow's meeting time.",
    "Text a friend asking to borrow their car this weekend.",
    "Group chat message asking where we should meet tonight.",
]


# ── Test generation ─────────────────────────────────────────

def _iter_cases():
    for display_name, model_id in MODELS:
        # Message not memo: multiple generations per prompt
        for prompt in MESSAGE_NOT_MEMO_PROMPTS:
            for rep in range(1, MNM_REPS + 1):
                yield pytest.param(
                    model_id, "message_not_memo", prompt, display_name, rep,
                    id=f"{display_name}::mnm::{prompt[:30]}::r{rep}"
                )
        # Full-coverage categories
        for category, prompts in [
            ("hard_asks", HARD_ASKS_PROMPTS),
            ("eq_tasks", EQ_TASKS_PROMPTS),
            ("story", STORY_PROMPTS),
        ]:
            for prompt in prompts:
                yield pytest.param(
                    model_id, category, prompt, display_name, None,
                    id=f"{display_name}::{category}::{prompt[:30]}"
                )
        # Communication control
        for prompt in COMMUNICATION_CONTROL_PROMPTS:
            yield pytest.param(
                model_id, "communication", prompt, display_name, None,
                id=f"{display_name}::communication::{prompt[:30]}"
            )


@pytest.mark.parametrize("model_id,category,prompt,display_name,rep", list(_iter_cases()))
def test_followup_validation(model_id, category, prompt, display_name, rep):
    actual = _run_model(model_id, prompt)
    tc = LLMTestCase(input=prompt, actual_output=actual)
    suffix = f" (rep {rep})" if rep else ""
    tc.name = f"[{category}] {display_name} | {prompt[:40]}{suffix}"

    metric_map = {
        "communication": _communication_metrics,
        "hard_asks": _hard_ask_metrics,
        "message_not_memo": _message_only_metrics,
        "eq_tasks": _eq_metrics,
        "story": _story_metrics,
    }
    assert_test(test_case=tc, metrics=metric_map[category]())
