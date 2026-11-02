"""LangGraph coordinator for routing banking requests to specialist agents."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from agent.accounts import get_account_balance
from agent.agent import BankingAgent
from agent.prompts import get_prompt
from agent.service import get_checkbook, get_customer_address, get_customer_credit_limit
from agent.transactions import get_account_transactions
from agent.tools import get_card_status, get_loan_status
from identity.authorization import use_principal
from llm.escalation import ThirdPartyReasoningModel
from llm.routing import requires_external_reasoning


class CoordinatorState(TypedDict):
    message: str
    history: list[dict]
    principal: dict[str, str]
    plan: list[str]
    next_agent: int
    findings: list[tuple[str, object]]
    reply: str


INTENT_KEYWORDS = {
    "balance": ("balance", "checking", "savings", "account"),
    "transactions": ("transaction", "transactions", "spent", "purchase", "payment"),
    "service": ("checkbook", "checks", "address", "mailing", "credit limit", "credit-limit"),
    "card": ("card", "debit"),
    "loan": ("loan", "borrow", "lending"),
}


def _keyword_plan(message: str) -> list[str]:
    plan = [
        name
        for name, keywords in INTENT_KEYWORDS.items()
        if any(keyword in message for keyword in keywords)
    ]
    if "credit limit" in message or "credit-limit" in message:
        plan = [name for name in plan if name != "card"]
    return plan


def _plan(state: CoordinatorState) -> dict:
    return {"plan": _keyword_plan(state["message"].lower()), "next_agent": 0}


def _dispatch(state: CoordinatorState) -> dict:
    if state["next_agent"] >= len(state["plan"]):
        return {}
    specialist_name = state["plan"][state["next_agent"]]
    message = state["message"].lower()
    with use_principal(state["principal"]):
        if specialist_name == "balance":
            accounts = []
            if "checking" in message or "savings" not in message:
                accounts.append("checking")
            if "savings" in message:
                accounts.append("savings")
            result = {account: get_account_balance(account) for account in accounts}
        elif specialist_name == "transactions":
            result = get_account_transactions()
        elif specialist_name == "service":
            if "credit limit" in message or "credit-limit" in message:
                result = get_customer_credit_limit()
            elif "checkbook" in message or "check" in message:
                result = get_checkbook()
            else:
                result = get_customer_address()
        elif specialist_name == "card":
            result = get_card_status()
        else:
            result = get_loan_status()
    return {
        "findings": [*state["findings"], (specialist_name, result)],
        "next_agent": state["next_agent"] + 1,
    }


def _route(state: CoordinatorState) -> str:
    if state["next_agent"] < len(state["plan"]):
        return "dispatch"
    return "respond"


def _respond(state: CoordinatorState) -> dict:
    message = state["message"]
    history = state["history"]
    if history and history[-1].get("role") == "user" and history[-1].get("content") == message:
        history = history[:-1]

    if state["findings"]:
        findings = "\n".join(f"{name}: {result}" for name, result in state["findings"])
        prompt = (
            f"User request: {message}\n"
            f"Verified tool results: {findings}\n\n"
            "Answer using only these verified results. If they do not contain "
            "the information requested, say what is unavailable. Be concise and friendly."
        )
    else:
        prompt = message

    with use_principal(state["principal"]):
        if requires_external_reasoning(message):
            reply = ThirdPartyReasoningModel().generate(
                prompt,
                history,
                system_instruction=get_prompt("complex_reasoning").text,
            )
        else:
            reply = BankingAgent().run(prompt, history)
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

    def run(self, message: str, history: list[dict], principal: dict[str, str]) -> str:
        result = self._graph.invoke(
            {
                "message": message,
                "history": history,
                "principal": principal,
                "plan": [],
                "next_agent": 0,
                "findings": [],
                "reply": "",
            }
        )
        return result["reply"]