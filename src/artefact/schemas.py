from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
