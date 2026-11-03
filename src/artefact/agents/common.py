from typing import Literal

from langchain.agents.middleware import AgentMiddleware, wrap_model_call
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from pydantic import BaseModel

SpecialistName = Literal["catalog", "orders", "policy"]


class Task(BaseModel):
    agent: SpecialistName
    question: str


class OutOfScopeItem(BaseModel):
    question: str
    reason: Literal["related", "unrelated"]


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class SpecialistInput(BaseModel):
    history: list[Turn]
    message: str
    question: str
    feedback: str | None


def to_turns(messages: list[BaseMessage]) -> list[Turn]:
    turns = []
    for message in messages:
        if isinstance(message, AIMessage):
            role = "assistant"
        else:
            role = "user"
        turns.append(Turn(role=role, content=message.text))
    return turns


def specialist_input(payload: dict) -> SpecialistInput:
    # payload is what orchestrator.send_tasks puts in each Send.
    return SpecialistInput(
        history=to_turns(payload["messages"][:-1]),
        message=payload["messages"][-1].text,
        question=payload["task"].question,
        feedback=payload["feedback"],
    )


def tool_call_budget(max_calls: int) -> AgentMiddleware:
    def limit_tools(request, handler):
        tool_results = 0
        for message in request.messages:
            if isinstance(message, ToolMessage):
                tool_results += 1
        if tool_results >= max_calls:
            request = request.override(tools=[])
        return handler(request)

    return wrap_model_call(limit_tools)
