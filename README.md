---
title: Agentic Honey Pot
emoji: 🍯
colorFrom: yellow
colorTo: red
sdk: docker
app_port: 7860
app_file: main.py
python_version: 3.11
pinned: false
---

# 🍯 Agentic Honey-Pot

An AI-powered scam honeypot API that detects, engages, and extracts intelligence from scammers — built for the GUVI Hackathon evaluation.

## Description

This system acts as a convincing scam victim that:
1. **Detects** incoming scam attempts using LLM-based classification
2. **Engages** the scammer naturally using an adaptive AI persona
3. **Extracts** intelligence (UPI IDs, phone numbers, account numbers, case IDs, etc.) across every conversation turn

The goal is to waste the scammer's time, elicit identifying information, and produce a structured intelligence report — all automatically.

## Tech Stack

- **Framework:** FastAPI (Python 3.11+)
- **LLM Provider:** Groq (primary) → Google Gemini (fallback)
- **Detection:** LLM zero-shot classification with RAG-augmented context (ChromaDB + sentence-transformers)
- **Session:** In-memory session management with conversation restore
- **Deployment:** Hugging Face Spaces (Docker)

## Architecture

```
Incoming Message
     │
     ▼
┌─────────────────┐
│ Detection Phase │  LLM classifies: is this a scam? What type?
└────────┬────────┘
         │ scam detected
         ▼
┌─────────────────┐
│ Engagement Phase│  Adaptive persona + goal tracker asks probing questions
└────────┬────────┘    (runs parallel with Investigator via asyncio.gather)
         │
         ▼
┌──────────────────────┐
│ Intelligence Phase   │  LLM extracts: UPI, phone, bank, caseIds, links, etc.
└──────────────────────┘
         │
         ▼
Structured JSON Response (GUVI format)
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YASHWANTH-SVNIT/Agentic-Honey-Pot.git
cd Agentic-Honey-Pot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

Required:
- `GROQ_API_KEY` — from [console.groq.com](https://console.groq.com)

Optional (fallback):
- `GEMINI_API_KEY` — from [aistudio.google.com](https://aistudio.google.com)
- `API_KEY` — custom key for protecting your endpoint (sent as `x-api-key` header)

### 4. Run the application
```bash
uvicorn main:app --host 0.0.0.0 --port 7860 --reload
```

API docs available at: `http://localhost:7860/docs`

## API Endpoint

- **URL:** `https://<your-hf-space>.hf.space/api/message`
- **Method:** `POST`
- **Authentication:** `x-api-key: <your-api-key>` (if API_KEY is set)

### Request Format
```json
{
  "sessionId": "session_abc123",
  "message": {
    "text": "Hello, this is Officer Sharma from CBI. Your account is under investigation.",
    "sender": "user",
    "timestamp": 1708435200000
  },
  "conversationHistory": [],
  "metadata": {}
}
```

### Response Format
```json
{
  "sessionId": "session_abc123",
  "status": "success",
  "scamDetected": true,
  "scamType": "digital_arrest",
  "confidenceLevel": 0.95,
  "reply": "Oh no... am I in trouble? What should I do?",
  "action": "engage",
  "agentNotes": "Scam type: digital_arrest. Red flags: impersonation of CBI officer; urgency/threat tactics; no verifiable badge number.",
  "extractedIntelligence": {
    "phoneNumbers": ["+91-9876543210"],
    "upiIds": ["officer.sharma@fakebank"],
    "bankAccounts": [],
    "phishingLinks": [],
    "emailAddresses": [],
    "caseIds": ["CBI-2024-1234"],
    "policyNumbers": [],
    "orderNumbers": [],
    "suspiciousKeywords": ["arrest", "money laundering", "urgent"],
    "amounts": [],
    "bankNames": [],
    "ifscCodes": []
  },
  "totalMessagesExchanged": 4,
  "engagementDurationSeconds": 120,
  "engagementMetrics": {
    "engagementDurationSeconds": 120,
    "totalMessagesExchanged": 4
  }
}
```

## Approach

### Scam Detection
- LLM zero-shot classification with a detailed prompt covering 15+ Indian scam categories
- RAG-augmented context using ChromaDB + sentence-transformers for pattern matching
- Confidence scoring and category assignment on first message

### Intelligence Extraction
- Dedicated `InvestigatorAgent` runs on every turn using LLM structured output
- Extracts 11 categories: UPI IDs, phone numbers, bank accounts, amounts, bank names, IFSC codes, phishing links, email addresses, case IDs, policy numbers, order numbers
- Uses disambiguation rules (context-aware) to avoid false positives
- Accumulates intel across all conversation turns

### Engagement Strategy
- Dynamic persona generator creates a believable victim profile
- Goal tracker identifies missing intel and generates natural extraction questions
- Anti-detection module prevents repetitive response patterns
- Investigative questions woven naturally: asks for badge ID, company website, officer name
- Runs parallel to intel extraction for minimal latency

## Health Check

```
GET /health
```

Returns system status, session count, and LLM provider availability.

## Project Structure

```
├── main.py                          # FastAPI app entry point
├── settings.py                      # Configuration and environment variables
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── data/
│   └── scam_dataset.json            # Scam pattern knowledge base
├── app/
│   ├── api/routes/
│   │   ├── message.py               # Main /api/message endpoint
│   │   └── health.py                # Health check endpoint
│   ├── models/
│   │   ├── schemas.py               # Request/response Pydantic models
│   │   └── session.py               # Session data model
│   └── services/
│       ├── detection/               # Scam detection pipeline
│       ├── engagement/              # Engagement agent + prompt builder
│       ├── intelligence/            # Intel extraction (InvestigatorAgent)
│       ├── llm/                     # Unified LLM client (Groq + Gemini)
│       ├── rag/                     # Vector store (ChromaDB)
│       ├── session/                 # Session management
│       └── finalization/            # Post-conversation processing
```
