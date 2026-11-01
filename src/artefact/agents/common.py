from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage
from pydantic import BaseModel

SpecialistName = Literal["catalog", "orders", "policy"]


class Task(BaseModel):
    agent: SpecialistName
    question: str
 

class OutOfScopeItem(BaseModel):
    question: str
    reason: Literal["accessories", "unrelated"]


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
