from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from artefact import orchestrator
from artefact.schemas import ChatRequest, ChatResponse

load_dotenv()

app = FastAPI(title="Empório da Música Agent")

@app.post("/invoke", response_model=ChatResponse)
def invoke(request: ChatRequest) -> ChatResponse:
    try:
        reply = orchestrator.run(request.session_id, request.message)
    except Exception:
        raise HTTPException(
            status_code=500, detail="Could not process the message"
        )
    return ChatResponse(reply=reply)
