"""
Global configuration for Agentic Honey-Pot
Loads environment variables and provides settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
# API Configuration
APP_X_API_KEY = os.getenv("APP_X_API_KEY")
API_KEY = APP_X_API_KEY
if not API_KEY:
    print("WARNING: APP_X_API_KEY not set in .env. using unsafe default for dev.")
    API_KEY = "honeypot_secret_key_2024"
    APP_X_API_KEY = API_KEY
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    print(f"[DEBUG] Settings loaded GROQ_API_KEY: {GROQ_API_KEY[:4]}...")
else:
    print("[ERROR] Settings: GROQ_API_KEY is MISSING or EMPTY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL_GROQ = os.getenv("LLM_MODEL_GROQ", "llama-3.3-70b-versatile")
LLM_MODEL_GEMINI = os.getenv("LLM_MODEL_GEMINI", "gemini-pro")

# Vector Store Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Session Configuration
USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))

# GUVI Integration
GUVI_API_KEY = os.getenv("GUVI_API_KEY")
GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL", "https://hackathon.guvi.in/api/updateHoneyPotFinalResult")

# Detection Thresholds
NORMAL_MODE_THRESHOLD = float(os.getenv("NORMAL_MODE_THRESHOLD", "0.7"))
STRICT_MODE_THRESHOLD = float(os.getenv("STRICT_MODE_THRESHOLD", "0.85"))
PROBE_THRESHOLD_MIN = float(os.getenv("PROBE_THRESHOLD_MIN", "0.5"))

# Engagement Configuration
MAX_TURNS = int(os.getenv("MAX_TURNS", "20"))
INTELLIGENCE_EXTRACTION_MIN_TURNS = int(os.getenv("INTELLIGENCE_EXTRACTION_MIN_TURNS", "8"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "honeypot.log")

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "hi"]

# Response Configuration
STRICT_RESPONSE_MODE = os.getenv("STRICT_RESPONSE_MODE", "false").lower() == "true"
