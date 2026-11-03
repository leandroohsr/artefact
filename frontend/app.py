import uuid
from pathlib import Path

import httpx
import streamlit as st

API_URL = "http://127.0.0.1:8000"
# Rendered in an iframe so the loader's own <body> styles and script do not touch the app.
LOADER = Path(__file__).parent / "loader.html"
ERROR_REPLY = "Desculpe, não consegui responder agora. Tente de novo em instantes."


def loader_html() -> str:
    html = LOADER.read_text(encoding="utf-8")
    # The iframe cannot see the app theme, so the notes get a light color in dark mode.
    if st.context.theme.type == "dark":
        html = html.replace("--ink: #1a1a1a", "--ink: #fafafa")
    return html


def ask(session_id: str, message: str) -> str:
    try:
        response = httpx.post(
            f"{API_URL}/invoke",
            json={"session_id": session_id, "message": message},
            timeout=120,
        )
    except httpx.HTTPError:
        return "Não consegui falar com o servidor. Ele está rodando (uv run artefact)?"
    if response.status_code != 200:
        return ERROR_REPLY
    return response.json()["reply"]


st.set_page_config(page_title="Empório da Música", page_icon="𝄞")
st.title("𝄞 Empório da Música")
st.caption("Produtos, pedidos e políticas da loja")

# One session_id per browser tab, so the backend keeps this conversation's context.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

text = st.chat_input("Digite sua mensagem")
if text:
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.markdown(text)

    with st.chat_message("assistant"):
        # Shown while the API answers, then replaced by the reply.
        loader = st.empty()
        with loader:
            st.iframe(loader_html(), height=40)
        reply = ask(st.session_state.session_id, text)
        loader.empty()
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
