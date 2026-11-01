from functools import cache
from typing import Annotated

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send

from artefact.agents.catalog.node import CatalogAgent
from artefact.agents.common import OutOfScopeItem, Task
from artefact.agents.delivery.node import DeliveryAgent
from artefact.agents.evaluator.node import EvaluatorAgent
from artefact.agents.evaluator.schema import EvaluatorOutput
from artefact.agents.orders.node import OrdersAgent
from artefact.agents.policy.node import PolicyAgent
from artefact.agents.router.node import RouterAgent

MAX_REVISIONS = 2


def merge_results(old: dict, new: dict | None) -> dict:
    if new is None:
        return {}
    merged = dict(old)
    merged.update(new)
    return merged


class State(MessagesState):
    tasks: list[Task]
    out_of_scope: list[OutOfScopeItem]
    results: Annotated[dict[str, dict], merge_results]
    draft: str
    feedback: str | None
    evaluation: EvaluatorOutput | None
    revisions: int


def send_tasks(state: State, tasks: list[Task]) -> list[Send]:
    # each send runs one specialist node in parallel
    sends = []
    for task in tasks:
        payload = {
            "task": task,
            "messages": state["messages"],
            "feedback": state["feedback"],
        }
        sends.append(Send(task.agent, payload))
    return sends


def classify_task(state: State) -> list[Send] | str:
    if not state["tasks"]:
        return "delivery"
    return send_tasks(state, state["tasks"])


def route_after_evaluation(state: State) -> list[Send] | str:
    evaluation = state["evaluation"]
    if evaluation.approved:
        return END
    if state["revisions"] > MAX_REVISIONS:
        return "fallback"
    if evaluation.retry_tasks:
        return send_tasks(state, evaluation.retry_tasks)
    return "delivery"


def fallback(state: State) -> dict:
    pass


@cache
def graph() -> CompiledStateGraph:
    builder = StateGraph(State)

    builder.add_node("router", RouterAgent())
    builder.add_node("catalog", CatalogAgent())
    builder.add_node("orders", OrdersAgent())
    builder.add_node("policy", PolicyAgent())
    builder.add_node("delivery", DeliveryAgent())
    builder.add_node("evaluator", EvaluatorAgent())
    builder.add_node("fallback", fallback)

    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router", classify_task, ["catalog", "orders", "policy", "delivery"]
    )
    builder.add_edge("catalog", "delivery")
    builder.add_edge("orders", "delivery")
    builder.add_edge("policy", "delivery")
    builder.add_edge("delivery", "evaluator")
    builder.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        [END, "fallback", "catalog", "orders", "policy", "delivery"],
    )
    builder.add_edge("fallback", END)

    return builder.compile()


def run(session_id: str, message: str) -> str:
    result = graph().invoke(
        {
            "messages": [HumanMessage(message)],
            "tasks": [],
            "out_of_scope": [],
            "results": None,
            "draft": "",
            "feedback": None,
            "evaluation": None,
            "revisions": 0,
        },
        {"configurable": {"thread_id": session_id}},
    )
    return result["messages"][-1].text
