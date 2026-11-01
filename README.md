# Empório da Música - Desafio técnico

uv run uvicorn app.main:app --reload


# How to run

uv run uvicorn artefact.api:app --reload or uv run artefact



curl -X POST http://127.0.0.1:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"session_id": "teste-1", "message": "Quanto custa o Takamine?"}'
