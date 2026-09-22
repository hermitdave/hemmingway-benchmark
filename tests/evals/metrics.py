from deepeval.metrics import (
    AnswerRelevancyMetric,
    GEval,
)
from deepeval.test_case.llm_test_case import SingleTurnParams
from deepeval.models import OpenAIModel

# Judge: Nous Portal (meituan/longcat-2.0:free)
judge = OpenAIModel(
    model="meituan/longcat-2.0:free",
    base_url="https://inference-api.nousresearch.com/v1",
    api_key="sk-nous-Zs3IKWNACb1ykmkTgiAz9vhNlSXr4Ob2",
)
# Alias for chatbot/summarization tests
_judge = judge

# Single-turn metrics using the judge
SINGLE_TURN_METRICS = [
    AnswerRelevancyMetric(model=judge, threshold=0.5),
    GEval(
        name="Correctness",
        criteria="Evaluate whether the actual output is factually correct and fully answers the input question. Consider accuracy, completeness, and relevance.",
        evaluation_steps=[
            "Check if the actual_output directly addresses the input question",
            "Verify factual correctness of claims made in the output",
            "Assess completeness - does it fully answer or leave gaps?",
            "Output a score from 0-1 based on overall correctness"
        ],
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        model=judge,
        threshold=0.5,
    ),
]
