from pydantic import BaseModel


class PolicyOutput(BaseModel):
    facts: list[str]
    sections: list[str]
