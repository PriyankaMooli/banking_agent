"""Complexity policy keeps routine prompts local and flags analysis."""

from llm.routing import requires_external_reasoning


def test_simple_lookup_stays_on_local_model():
    assert not requires_external_reasoning("What is my checking balance?")


def test_comparison_is_escalated():
    assert requires_external_reasoning(
        "Compare my checking and savings balances and explain the difference"
    )


def test_multi_question_request_is_escalated():
    assert requires_external_reasoning(
        "What did I spend on groceries? Also, why is my balance lower?"
    )
