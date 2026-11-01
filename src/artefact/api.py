import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response

from artefact import orchestrator
from artefact.data import DATA_DIR, DATA_FILES
from artefact.data.catalog import catalog, search_index
from artefact.data.policies import load_policies
from artefact.llm import get_llm
from artefact.schemas import ChatRequest, ChatResponse

logging.basicConfig(format="%(levelname)s:     %(name)s: %(message)s")
logging.getLogger("artefact").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        catalog()
        search_index()
        load_policies()
        get_llm()
    except Exception:
        logger.exception("Warm-up failed")
    yield


app = FastAPI(title="Empório da Música Agent", lifespan=lifespan)


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
    if all(checks.values()):
        return {"status": "ok", "checks": checks}

    response.status_code = 503
    return {"status": "unavailable", "checks": checks}


@app.post("/invoke", response_model=ChatResponse)
def invoke(request: ChatRequest) -> ChatResponse:
    try:
        reply = orchestrator.run(request.session_id, request.message)
    except Exception:
        logger.exception("Failed to process message for session %s", request.session_id)
        raise HTTPException(status_code=500, detail="Could not process the message")
    return ChatResponse(reply=reply)
