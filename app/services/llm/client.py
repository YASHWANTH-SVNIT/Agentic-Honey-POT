"""
Dual LLM Client - Separate clients for Engagement vs Extraction
- Engagement: Creative responses, uses dedicated Groq key
- Extraction: Structured JSON parsing, uses separate Groq key (isolated quota)
"""
import json
import re
import httpx
from typing import Dict, Any, Optional
import settings

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Groq import failed: {e}")
    GROQ_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
    GENAI_NEW = True
except ImportError:
    GENAI_NEW = False
    try:
        import google.generativeai as genai
        GENAI_AVAILABLE = True
    except ImportError:
        GENAI_AVAILABLE = False


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model configurations for different tasks
ENGAGEMENT_MODEL = "google/gemini-2.0-flash-001"  # Creative, natural responses
EXTRACTION_MODEL = "google/gemini-2.0-flash-001"  # Structured JSON output


def _call_openrouter(prompt: str, temperature: float, max_tokens: int, model: str) -> Optional[str]:
    """Call OpenRouter API (OpenAI-compatible)"""
    if not settings.OPENROUTER_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/agentic-honeypot",
        "X-Title": "Agentic Honey-Pot"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] OpenRouter API error: {e}")
        return None


def _extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON from LLM response"""
    # Try to find JSON in code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find raw JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = text

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing error: {e}")
        print(f"Response text: {text[:500]}...")
        return {
            "is_scam": False,
            "confidence": 0.0,
            "primary_category": None,
            "reasoning": "Failed to parse LLM response",
            "error": str(e)
        }


class EngagementLLM:
    """LLM client optimized for engagement (creative victim responses)

    Uses dedicated Groq key (GROQ_API_KEY_ENGAGEMENT) to isolate from extraction quota.
    """

    def __init__(self):
        self.groq_client = None
        self.gemini_client = None
        self.use_new_genai = GENAI_NEW

        # Get engagement-specific key, fallback to general key
        engagement_key = getattr(settings, 'GROQ_API_KEY_ENGAGEMENT', None) or settings.GROQ_API_KEY

        # Primary: Groq with dedicated engagement key
        if GROQ_AVAILABLE and engagement_key:
            try:
                self.groq_client = Groq(api_key=engagement_key)
                self.groq_model = settings.LLM_MODEL_GROQ
                print(f"[Engagement LLM] Groq initialized with key: {engagement_key[:8]}...")
            except Exception as e:
                print(f"[Engagement LLM] Groq failed: {e}")

        # Fallback: Gemini
        if GENAI_AVAILABLE and settings.GOOGLE_API_KEY:
            try:
                if self.use_new_genai:
                    self.gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
                    self.gemini_model = settings.LLM_MODEL_GEMINI
                else:
                    genai.configure(api_key=settings.GOOGLE_API_KEY)
                    self.gemini_client = genai.GenerativeModel(settings.LLM_MODEL_GEMINI)
                print("[Engagement LLM] Gemini initialized (fallback)")
            except Exception as e:
                print(f"[Engagement LLM] Gemini failed: {e}")

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate creative response for engagement"""

        # Try Groq first (dedicated engagement key)
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"[Engagement LLM] Groq error: {e}")

        # Try OpenRouter
        result = _call_openrouter(prompt, temperature, max_tokens, ENGAGEMENT_MODEL)
        if result:
            return result

        # Try Gemini
        if self.gemini_client:
            try:
                if self.use_new_genai:
                    response = self.gemini_client.models.generate_content(
                        model=self.gemini_model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens
                        )
                    )
                    return response.text
                else:
                    response = self.gemini_client.generate_content(prompt)
                    return response.text
            except Exception as e:
                print(f"[Engagement LLM] Gemini error: {e}")

        return "I didn't quite understand. Could you please explain again?"


class ExtractionLLM:
    """LLM client optimized for extraction (structured JSON output)

    Uses dedicated Groq key (GROQ_API_KEY_EXTRACTION) to isolate from engagement quota.
    Primary: OpenRouter, Fallback: Groq with extraction key
    """

    def __init__(self):
        self.groq_client = None

        # OpenRouter as primary (cheap, isolated)
        self.has_openrouter = bool(settings.OPENROUTER_API_KEY)
        if self.has_openrouter:
            print("[Extraction LLM] OpenRouter initialized (primary)")

        # Get extraction-specific key, fallback to general key
        extraction_key = getattr(settings, 'GROQ_API_KEY_EXTRACTION', None) or settings.GROQ_API_KEY

        # Fallback: Groq with dedicated extraction key
        if GROQ_AVAILABLE and extraction_key:
            try:
                self.groq_client = Groq(api_key=extraction_key)
                self.groq_model = settings.LLM_MODEL_GROQ
                print(f"[Extraction LLM] Groq initialized with key: {extraction_key[:8]}... (fallback)")
            except Exception as e:
                print(f"[Extraction LLM] Groq failed: {e}")

    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 1500) -> str:
        """Generate structured response for extraction (low temperature for consistency)"""

        # Try OpenRouter first (isolated quota)
        if self.has_openrouter:
            result = _call_openrouter(prompt, temperature, max_tokens, EXTRACTION_MODEL)
            if result:
                return result

        # Fallback to Groq (dedicated extraction key)
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"[Extraction LLM] Groq error: {e}")

        return "{}"

    def generate_json(self, prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        """Generate and parse JSON response"""
        response_text = self.generate(prompt, temperature=temperature, max_tokens=1500)
        return _extract_json(response_text)


# Legacy unified client for backward compatibility
class LLMClient:
    """Unified LLM client (legacy) - wraps engagement + extraction LLMs"""

    def __init__(self):
        self._engagement = EngagementLLM()
        self._extraction = ExtractionLLM()

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        return self._engagement.generate(prompt, temperature, max_tokens)

    def generate_json(self, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        return self._extraction.generate_json(prompt, temperature)


# Global instances
_engagement_llm: Optional[EngagementLLM] = None
_extraction_llm: Optional[ExtractionLLM] = None
_llm_client: Optional[LLMClient] = None


def get_engagement_llm() -> EngagementLLM:
    """Get engagement LLM (for generating victim responses)"""
    global _engagement_llm
    if _engagement_llm is None:
        _engagement_llm = EngagementLLM()
    return _engagement_llm


def get_extraction_llm() -> ExtractionLLM:
    """Get extraction LLM (for parsing intelligence from messages)"""
    global _extraction_llm
    if _extraction_llm is None:
        _extraction_llm = ExtractionLLM()
    return _extraction_llm


def get_llm_client() -> LLMClient:
    """Get unified LLM client (legacy compatibility)"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
