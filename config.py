import os
from dotenv import load_dotenv

load_dotenv()

# ── Mode ──────────────────────────────────────────────
EVA_MODE = "offline"          # "offline" | "online" | "hybrid"
ASK_BEFORE_ONLINE = True      # If True, EVA asks permission before using online APIs

# ── LLM ───────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral"      # or "llama3"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Voice ─────────────────────────────────────────────
TTS_ENGINE = "pyttsx3"        # "pyttsx3" | "elevenlabs"
STT_ENGINE = "google"         # "google" | "whisper"
WAKE_WORD = "eva"             # Future phase

# ── Memory ────────────────────────────────────────────
MEMORY_DB_PATH = "eva/memory/eva_memory.db"

# ── Logging ───────────────────────────────────────────
LOG_LEVEL = "INFO"            # "DEBUG" | "INFO" | "WARNING"
LOG_FILE = "eva/logs/eva.log"

# ── Assistant Personality ─────────────────────────────
EVA_NAME = "EVA"
RESPONSE_STYLE = "hinglish"   # "hinglish" | "english"
