from pydantic import BaseModel

from artefact.agents.common import OutOfScopeItem, Task, Turn


class EvaluatorInput(BaseModel):
    history: list[Turn]
    message: str
    tasks: list[Task]
    results: dict[str, dict]
    out_of_scope: list[OutOfScopeItem]
    draft: str


class EvaluatorOutput(BaseModel):
    approved: bool
    issues: list[str]
    retry_tasks: list[Task]
    feedback: str
