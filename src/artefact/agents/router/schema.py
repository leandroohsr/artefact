from pydantic import BaseModel, field_validator

from artefact.agents.common import OutOfScopeItem, Task, Turn


class RouterInput(BaseModel):
    history: list[Turn]
    message: str


class RouterOutput(BaseModel):
    tasks: list[Task]
    out_of_scope: list[OutOfScopeItem]

    @field_validator("tasks")
    @classmethod
    def one_task_per_agent(cls, tasks: list[Task]) -> list[Task]:
        #  before: tasks = [Task(agent="catalog", question="preço do GD20"), Task(agent="catalog", question="estoque do C40")]
        #  now: tasks = [Task(agent="catalog", question="preço do GD20 estoque do C40")]

        merged: dict[str, Task] = {}
        for task in tasks:
            if task.agent in merged:
                merged[task.agent].question += f" {task.question}"
            else:
                merged[task.agent] = task.model_copy()
        return list(merged.values())
