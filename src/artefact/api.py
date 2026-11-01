import logging

from fastapi import FastAPI, HTTPException, Response

from artefact import orchestrator
from artefact.data import DATA_DIR, DATA_FILES
from artefact.llm import get_llm
from artefact.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="Empório da Música Agent")


def llm_ready() -> bool:
    # only checks LLM_MODEL
    try:
        get_llm()
    except Exception:
        logger.exception("Health check: LLM is not configured")
        return False
    return True


@app.get("/health")
def health(response: Response) -> dict:
    checks = {
        "llm": llm_ready(),
        "data_files": all((DATA_DIR / name).is_file() for name in DATA_FILES),
    }
    healthy = all(checks.values())
    if not healthy:
        response.status_code = 503
    return {"status": "ok" if healthy else "unavailable", "checks": checks}


@app.post("/invoke", response_model=ChatResponse)
def invoke(request: ChatRequest) -> ChatResponse:
    try:
        reply = orchestrator.run(request.session_id, request.message)
    except Exception:
        logger.exception("Failed to process message for session %s", request.session_id)
        raise HTTPException(status_code=500, detail="Could not process the message")
    return ChatResponse(reply=reply)
