import os

from dotenv import load_dotenv

load_dotenv()


LLM_MODEL = os.getenv("LLM_MODEL")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "16000"))
