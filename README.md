# Empório da Música - Desafio técnico

uv run uvicorn app.main:app --reload


# How to run

uv run uvicorn artefact.api:app --reload or uv run artefact


## Catalog Agent
curl -X POST http://127.0.0.1:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"session_id": "teste-1", "message": "Quanto custa o Takamine?"}'

## Order Agent
curl -X POST http://127.0.0.1:8000/invoke -H "Content-Type: application/json" \
  -d '{"session_id": "t1", "message": "Oi, qual o status do meu pedido 7? Meu e-mail é leticia.rocha@jmail.com"}'

curl -X POST http://127.0.0.1:8000/invoke -H "Content-Type: application/json" \
  -d '{"session_id": "p2", "message": "Vocês parcelam em quantas vezes? Tem desconto no PIX?"}'

curl -X POST http://127.0.0.1:8000/invoke -H "Content-Type: application/json" \
  -d '{"session_id": "p3", "message": "Qual o endereço da loja e que horas abre no sábado?"}'

curl -X POST http://127.0.0.1:8000/invoke -H "Content-Type: application/json" \
  -d '{"session_id": "p4", "message": "Quanto custa o Yamaha C40 e qual a garantia?"}'


### Teste Router Agent:
uv run python -c "
from langchain_core.messages import HumanMessage
from artefact.agents.router.node import RouterAgent

out = RouterAgent()({'messages': [HumanMessage('Quanto custa o Takamine GD20 e dá pra parcelar em 12x?')]})
print(out)
"





