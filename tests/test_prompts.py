"""Every agent prompt must have version and change metadata."""

import re

import pytest

from agent.prompts import PROMPTS, get_prompt


def test_all_agent_prompts_are_versioned_and_documented():
    expected_prompts = {
        "banking_response",
        "intent_classifier",
        "accounts_specialist",
        "service_specialist",
        "transactions_specialist",
        "complex_reasoning",
    }

    assert set(PROMPTS) == expected_prompts
    for prompt in PROMPTS.values():
        assert re.fullmatch(r"\d+\.\d+\.\d+", prompt.version)
        assert prompt.text.strip()
        assert prompt.change_note.strip()


def test_unknown_prompt_name_is_rejected():
    with pytest.raises(ValueError, match="Unknown prompt name"):
        get_prompt("missing_agent")
