"""LangGraph coordinator for routing banking requests to specialist agents."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from agent.accounts import AccountsAgent
from agent.agent import BankingAgent
from agent.service import ServiceAgent
from agent.transactions import TransactionsAgent
from agent.tools import (
    get_balance,
    get_card_status,
    get_loan_status,
    get_recent_transactions,
)


class CoordinatorState(TypedDict):
    message: str
    history: list[dict]
    plan: list[str]
    next_agent: int
    findings: list[tuple[str, object]]
    reply: str


SPECIALISTS = {
    "balance": get_balance,
    "transactions": get_recent_transactions,
    "card": get_card_status,
    "loan": get_loan_status,
}

INTENT_KEYWORDS = {
    "balance": ("balance", "checking", "savings", "account"),
    "transactions": ("transaction", "transactions", "spent", "purchase", "payment"),
    "service": ("checkbook", "checks", "address", "mailing", "credit limit", "credit-limit"),
    "card": ("card", "debit"),
    "loan": ("loan", "borrow", "lending"),
}


def _plan(state: CoordinatorState) -> dict:
    message = state["message"].lower()
    plan = [
        name
        for name, keywords in INTENT_KEYWORDS.items()
        if any(keyword in message for keyword in keywords)
    ]
    if "credit limit" in message or "credit-limit" in message:
        plan = [name for name in plan if name != "card"]
    return {"plan": plan, "next_agent": 0}


def _dispatch(state: CoordinatorState) -> dict:
    if state["next_agent"] >= len(state["plan"]):
        return {}
    specialist_name = state["plan"][state["next_agent"]]
    if specialist_name == "balance":
        result = AccountsAgent().run(state["message"], state["history"])
    elif specialist_name == "transactions":
        result = TransactionsAgent().run(state["message"], state["history"])
    elif specialist_name == "service":
        result = ServiceAgent().run(state["message"], state["history"])
    else:
        result = SPECIALISTS[specialist_name]()
    return {
        "findings": [*state["findings"], (specialist_name, result)],
        "next_agent": state["next_agent"] + 1,
    }


def _route(state: CoordinatorState) -> str:
    if state["next_agent"] < len(state["plan"]):
        return "dispatch"
    return "respond"


def _respond(state: CoordinatorState) -> dict:
    if not state["findings"]:
        reply = BankingAgent().run(state["message"], state["history"])
    else:
        findings = "\n".join(f"{name}: {result}" for name, result in state["findings"])
        prompt = (
            f"User request: {state['message']}\n"
            f"Verified specialist results:\n{findings}\n\n"
            "Answer the user using only these verified results. Be concise and friendly."
        )
        reply = BankingAgent().run(prompt, state["history"])
    return {"reply": reply}


def _build_graph():
    graph = StateGraph(CoordinatorState)
    graph.add_node("plan", _plan)
    graph.add_node("dispatch", _dispatch)
    graph.add_node("respond", _respond)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "dispatch")
    graph.add_conditional_edges("dispatch", _route, {"dispatch": "dispatch", "respond": "respond"})
    graph.add_edge("respond", END)
    return graph.compile()


class CoordinatorAgent:
    """Plan and run the specialist agents needed for a banking request."""

    def __init__(self) -> None:
        self._graph = _build_graph()

    def run(self, message: str, history: list[dict]) -> str:
        result = self._graph.invoke(
            {
                "message": message,
                "history": history,
                "plan": [],
                "next_agent": 0,
                "findings": [],
                "reply": "",
            }
        )
        return result["reply"]