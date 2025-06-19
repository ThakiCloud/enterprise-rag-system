from pathlib import Path
import os

# --- Directories ---
BASE_DIR = Path(__file__).resolve().parent.parent
TMP_DIR = BASE_DIR.parent / "tmp"
UPLOAD_DIR = TMP_DIR / "uploads"
VECTOR_DB_PATH = TMP_DIR / "lancedb"
DB_FILE = TMP_DIR / "enterprise_rag.db"

# --- Create directories if they don't exist ---
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

# --- Dynamic Model Provider Configuration ---
# Set the provider using an environment variable: "openai", "anthropic", "google", "ollama", "vllm", "lm-studio"
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai").lower()

# --- OpenAI Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")

# --- Anthropic (Claude) Configuration ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL_NAME = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")

# --- Google (Gemini) Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-1.5-pro-latest")

# --- Ollama Configuration ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")

# --- LM Studio Configuration ---
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")

# --- vLLM / Other OpenAI-compatible APIs ---
# For services that expose an OpenAI-compatible endpoint.
CUSTOM_API_BASE_URL = os.getenv("CUSTOM_API_BASE_URL")  # e.g., http://localhost:8000/v1
CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY", "not-needed")
CUSTOM_MODEL_NAME = os.getenv("CUSTOM_MODEL_NAME")

# --- Agent IDs ---
RAG_AGENT_ID = "enterprise-rag-agent"
REASONING_AGENT_ID = "reasoning-specialist"
RESEARCH_TEAM_ID = "enterprise-research-team" 