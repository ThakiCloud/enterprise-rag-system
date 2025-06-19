import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
