"""
Global configuration for Agentic Honey-Pot
Loads environment variables and provides settings
"""
import os
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
load_dotenv()

# API Configuration
APP_X_API_KEY = os.getenv("APP_X_API_KEY")
API_KEY = APP_X_API_KEY
if not API_KEY:
    print("WARNING: APP_X_API_KEY not set in .env. Using unsafe default for dev.")
    API_KEY = "honeypot_secret_key_2024"
    APP_X_API_KEY = API_KEY
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# LLM Configuration - Separate keys for Engagement vs Extraction
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

# Separate Groq keys for isolation
GROQ_API_KEY_ENGAGEMENT = os.getenv("GROQ_API_KEY_ENGAGEMENT")
GROQ_API_KEY_EXTRACTION = os.getenv("GROQ_API_KEY_EXTRACTION")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Legacy fallback

if GROQ_API_KEY_ENGAGEMENT:
    print(f"[Settings] GROQ Engagement Key: {GROQ_API_KEY_ENGAGEMENT[:8]}...")
if GROQ_API_KEY_EXTRACTION:
    print(f"[Settings] GROQ Extraction Key: {GROQ_API_KEY_EXTRACTION[:8]}...")
if GROQ_API_KEY:
    print(f"[Settings] GROQ Fallback Key: {GROQ_API_KEY[:8]}...")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if OPENROUTER_API_KEY:
    print(f"[Settings] OpenRouter Key: {OPENROUTER_API_KEY[:12]}...")

# Model Selection - Using best available models
LLM_MODEL_GROQ = os.getenv("LLM_MODEL_GROQ", "llama-3.3-70b-versatile")
LLM_MODEL_GEMINI = os.getenv("LLM_MODEL_GEMINI", "gemini-2.0-flash")
LLM_MODEL_OPENROUTER = os.getenv("LLM_MODEL_OPENROUTER", "google/gemini-2.0-flash-001")

# Vector Store Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(PROJECT_ROOT / "chroma_db"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Session Configuration
USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))

# GUVI Integration
GUVI_API_KEY = os.getenv("GUVI_API_KEY")
GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL", "https://hackathon.guvi.in/api/updateHoneyPotFinalResult")

# Detection Thresholds (SIMPLIFIED - NO STRICT MODE)
DETECTION_THRESHOLD = float(os.getenv("DETECTION_THRESHOLD", "0.75"))  # High confidence to engage
PROBE_THRESHOLD = float(os.getenv("PROBE_THRESHOLD", "0.55"))  # Medium confidence to probe

# Engagement Configuration
MAX_TURNS = int(os.getenv("MAX_TURNS", "20"))
MIN_INTELLIGENCE_TURNS = int(os.getenv("MIN_INTELLIGENCE_TURNS", "8"))

# Language Support (SIMPLIFIED - ENGLISH ONLY)
SUPPORTED_LANGUAGES = ["en", "unknown"]  # "unknown" gets benefit of doubt

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "honeypot.log")

print("[Settings] Configuration loaded successfully")
print(f"[Settings] LLM Provider: {LLM_PROVIDER}")
print(f"[Settings] Detection Threshold: {DETECTION_THRESHOLD}")
print(f"[Settings] Supported Languages: {SUPPORTED_LANGUAGES}")
print(f"[Settings] Max Turns: {MAX_TURNS}")
