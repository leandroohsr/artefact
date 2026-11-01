from pydantic import BaseModel

from artefact.agents.common import OutOfScopeItem, Task, Turn


class DeliveryInput(BaseModel):
    history: list[Turn]
    message: str
    tasks: list[Task]
    results: dict[str, dict]
    out_of_scope: list[OutOfScopeItem]
    feedback: str | None


class DeliveryOutput(BaseModel):
    reply: str
