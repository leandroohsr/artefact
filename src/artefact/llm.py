from functools import cache

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from artefact.config import LLM_EFFORT, LLM_MAX_TOKENS, LLM_MODEL


@cache
def get_llm() -> BaseChatModel:
    if not LLM_MODEL:
        raise RuntimeError("LLM_MODEL is not set in .env")

    options = {"max_tokens": LLM_MAX_TOKENS}
    if LLM_EFFORT:
        options["output_config"] = {"effort": LLM_EFFORT}

    return init_chat_model(LLM_MODEL, **options)
