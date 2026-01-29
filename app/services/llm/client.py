"""
Unified LLM Client supporting Groq and Google Gemini
Handles API calls with fallback logic
"""
import json
import re
from typing import Dict, Any, Optional
import settings

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Groq import failed: {e}")
    GROQ_AVAILABLE = False

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class LLMClient:
    """Unified LLM client with Groq primary and Gemini fallback"""
    
    def __init__(self):
        """Initialize LLM clients"""
        self.primary_client = None
        self.fallback_client = None
        
        # Initialize Groq (primary)
        if GROQ_AVAILABLE and settings.GROQ_API_KEY:
            try:
                self.primary_client = Groq(api_key=settings.GROQ_API_KEY)
                self.primary_model = settings.LLM_MODEL_GROQ
                print("[OK] Groq client initialized (primary)")
            except Exception as e:
                print(f"[ERROR] Groq initialization failed: {e}")
        
        # Initialize Gemini (fallback)
        if GENAI_AVAILABLE and settings.GOOGLE_API_KEY:
            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.fallback_client = genai.GenerativeModel(settings.LLM_MODEL_GEMINI)
                print("[OK] Gemini client initialized (fallback)")
            except Exception as e:
                print(f"[ERROR] Gemini initialization failed: {e}")
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate response from LLM with fallback"""
        # Try primary (Groq)
        if self.primary_client:
            try:
                response = self.primary_client.chat.completions.create(
                    model=self.primary_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"[ERROR] Groq API error: {e}")
        
        # Fallback to Gemini
        if self.fallback_client:
            try:
                response = self.fallback_client.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"[ERROR] Gemini API error: {e}")
        
        # Fallback for testing/no keys
        print("! No LLM client available. Returning mock response.")
        return "This is a mock response from the Agentic Honey-Pot. (No LLM keys configured)"
    
    def generate_json(self, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate JSON response from LLM"""
        response_text = self.generate(prompt, temperature=temperature, max_tokens=1500)
        return self._extract_json(response_text)
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
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
            # Return a default structure
            return {
                "is_scam": False,
                "confidence": 0.0,
                "primary_category": None,
                "reasoning": "Failed to parse LLM response",
                "error": str(e)
            }


# Global instance
_llm_client = None

def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
