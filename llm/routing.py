"""Local policy for deciding whether to escalate reasoning externally."""

import re


_COMPLEXITY_CUES = re.compile(
    r"\b(compare|comparison|analy[sz]e|analysis|trend|trends|forecast|"
    r"recommend|recommendation|relationship|impact|explain why|why did|"
    r"trade[- ]off|optimi[sz]e|plan|strategy|summari[sz]e)\b",
    re.IGNORECASE,
)
_QUESTION_SPLIT = re.compile(r"\?\s*\S")
_BANKING_TOPICS = (
    "balance",
    "transaction",
    "spending",
    "card",
    "loan",
    "credit limit",
    "checkbook",
    "address",
)


def requires_external_reasoning(message: str) -> bool:
    """Return whether a request has clear multi-step/analytical complexity."""
    if _COMPLEXITY_CUES.search(message):
        return True

    if len(_QUESTION_SPLIT.findall(message)) > 0:
        return True

    topic_count = sum(topic in message.lower() for topic in _BANKING_TOPICS)
    return topic_count >= 2
