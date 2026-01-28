# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

## 🎯 Project Overview

agentic_honey-pot/
│
├── README.md                          # Main documentation
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .env                              # Actual environment variables (gitignored)
├── .gitignore                        # Git ignore file
│
├── main.py                           # FastAPI application entry point
├── config.py                         # Configuration management
│
├── app/                              # Main application directory
│   ├── __init__.py
│   │
│   ├── api/                          # API layer
│   │   ├── __init__.py
│   │   ├── dependencies.py           # API dependencies (auth, session)
│   │   ├── middleware.py             # Custom middleware
│   │   └── routes/                   # API routes
│   │       ├── __init__.py
│   │       ├── message.py            # Main message endpoint
│   │       └── health.py             # Health check endpoint
│   │
│   ├── models/                       # Pydantic models
│   │   ├── __init__.py
│   │   ├── schemas.py                # Request/Response schemas
│   │   ├── session.py                # Session models
│   │   └── intelligence.py           # Intelligence data models
│   │
│   ├── services/                     # Business logic
│   │   ├── __init__.py
│   │   │
│   │   ├── session/                  # Session management
│   │   │   ├── __init__.py
│   │   │   ├── manager.py            # Session CRUD operations
│   │   │   └── store.py              # Session storage (Redis/Memory)
│   │   │
│   │   ├── detection/                # Detection pipeline
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py           # Main detection orchestrator
│   │   │   ├── pre_screen.py         # Pre-screening filters
│   │   │   ├── language_detector.py  # Language detection
│   │   │   ├── rag_retriever.py      # RAG evidence retrieval
│   │   │   ├── llm_detector.py       # LLM judgment
│   │   │   └── decision_maker.py     # Final decision logic
│   │   │
│   │   ├── engagement/               # Agent engagement
│   │   │   ├── __init__.py
│   │   │   ├── agent.py              # Main agent response generator
│   │   │   ├── persona_selector.py   # Persona selection logic
│   │   │   ├── stage_manager.py      # Stage progression
│   │   │   ├── stop_checker.py       # Stop condition checker
│   │   │   └── prompt_builder.py     # LLM prompt construction
│   │   │
│   │   ├── intelligence/             # Intelligence extraction
│   │   │   ├── __init__.py
│   │   │   ├── extractors.py         # Regex pattern extractors
│   │   │   ├── manager.py            # Intel storage management
│   │   │   └── analyzer.py           # Intel analysis
│   │   │
│   │   ├── rag/                      # RAG system
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py       # ChromaDB interface
│   │   │   ├── embedder.py           # Embedding model
│   │   │   ├── loader.py             # Dataset loader
│   │   │   └── query.py              # Query interface
│   │   │
│   │   ├── llm/                      # LLM client
│   │   │   ├── __init__.py
│   │   │   ├── client.py             # Base LLM client
│   │   │   ├── groq_client.py        # Groq implementation
│   │   │   ├── gemini_client.py      # Gemini implementation
│   │   │   └── anthropic_client.py   # Claude implementation
│   │   │
│   │   └── finalization/             # Session finalization
│   │       ├── __init__.py
│   │       ├── report_builder.py     # Intelligence report assembly
│   │       ├── guvi_callback.py      # GUVI API callback
│   │       └── archiver.py           # Session archival
│   │
│   ├── core/                         # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py                 # Configuration loader
│   │   ├── logging.py                # Logging setup
│   │   ├── exceptions.py             # Custom exceptions
│   │   └── utils.py                  # Utility functions
│   │
│   └── db/                           # Database/Storage
│       ├── __init__.py
│       ├── redis_client.py           # Redis connection
│       └── models.py                 # Database models (if using SQL)
│
├── data/                             # Data files
│   ├── scam_dataset.json             # 100-record scam dataset
│   ├── personas.json                 # Persona definitions
│   ├── extraction_targets.json       # Category-specific targets
│   └── stage_config.json             # Stage definitions
│
├── config/                           # Configuration files
│   ├── __init__.py
│   ├── personas.py                   # Persona mappings
│   ├── stages.py                     # Stage configurations
│   ├── extraction_targets.py         # Extraction target definitions
│   └── prompts.py                    # LLM prompt templates
│
├── chroma_db/                        # ChromaDB storage (auto-generated)
│   └── (vector database files)
│
├── logs/                             # Application logs
│   ├── app.log
│   ├── detection.log
│   ├── engagement.log
│   └── errors.log
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   │
│   ├── unit/                         # Unit tests
│   │   ├── __init__.py
│   │   ├── test_pre_screen.py
│   │   ├── test_language_detector.py
│   │   ├── test_extractors.py
│   │   ├── test_persona_selector.py
│   │   └── test_stage_manager.py
│   │
│   ├── integration/                  # Integration tests
│   │   ├── __init__.py
│   │   ├── test_detection_flow.py
│   │   ├── test_engagement_flow.py
│   │   ├── test_rag_system.py
│   │   └── test_guvi_callback.py
│   │
│   └── fixtures/                     # Test fixtures
│       ├── __init__.py
│       ├── sample_messages.py
│       └── mock_responses.py
│
├── scripts/                          # Utility scripts
│   ├── setup_database.py             # Initialize ChromaDB
│   ├── load_dataset.py               # Load scam dataset
│   ├── test_llm_connection.py        # Test LLM API
│   ├── test_guvi_callback.py         # Test GUVI endpoint
│   └── generate_sample_data.py       # Generate test data
│
└── docs/                             # Additional documentation
    ├── API.md                        # API documentation
    ├── WORKFLOW.md                   # Detailed workflow
    ├── DATASET.md                    # Dataset documentation
    ├── DEPLOYMENT.md                 # Deployment guide
    └── TROUBLESHOOTING.md            # Common issues

### Objective
Build an AI-powered honeypot system that:
1. **Detects** scam intent in incoming messages using RAG + LLM
2. **Engages** scammers autonomously with human-like personas
3. **Extracts** intelligence (UPI IDs, phone numbers, URLs, modus operandi)
4. **Reports** findings to GUVI evaluation API

### Core Innovation
**Two-Phase Architecture:**
- **Detection Phase:** RAG provides evidence → LLM makes final judgment (always)
- **Engagement Phase:** Context-aware agent adapts to scam category (no RAG)

### Key Principles
- ✅ **Simple & Predictable:** Single code path, LLM always validates
- ✅ **Language-Aware:** Normal mode (EN/HI) vs Strict mode (other languages)
- ✅ **Production-Safe:** Minimal pre-screening, robust error handling
- ✅ **Category-Driven:** Agent persona adapts based on detected scam type

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     Platform Request                            │
│              POST /api/message (with sessionId)                 │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                   API Server (FastAPI)                          │
│  ├─ API Key Validation                                          │
│  ├─ Schema Validation                                           │
│  └─ Session Management                                          │
└───────────────────────────┬────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌──────────────────┐    ┌──────────────────────┐
    │  NEW SESSION     │    │  EXISTING SESSION    │
    │  (Detection)     │    │  (Engagement)        │
    └──────┬───────────┘    └──────────┬───────────┘
           │                           │
           ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│ DETECTION PIPELINE   │    │ ENGAGEMENT PIPELINE  │
│                      │    │                      │
│ 1. Pre-screen        │    │ 1. Extract intel     │
│ 2. Language detect   │    │ 2. Update stage      │
│ 3. RAG retrieve      │    │ 3. Select persona    │
│ 4. LLM judge         │    │ 4. Generate reply    │
│ 5. Decision          │    │ 5. Check stop        │
└──────┬───────────────┘    └──────────┬───────────┘
       │                               │
       │ ENGAGE                        │ CONTINUE
       ▼                               ▼
┌─────────────────────────────────────────────┐
│         Agent Response Generated            │
│  (Category-specific persona, stage-based)   │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Intelligence Extracted              │
│  (UPI, Phone, URL, Keywords - Passive)      │
└──────────────────┬──────────────────────────┘
                   │
                   │ Stop Condition Met?
                   ▼
┌─────────────────────────────────────────────┐
│         Session Finalization                │
│  ├─ Assemble Intelligence Report            │
│  ├─ GUVI Callback (MANDATORY)               │
│  └─ Session Closure                         │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Technical Stack

### Core Framework
- **API Server:** FastAPI (Python 3.10+)
- **Agentic Logic:** LangGraph (optional) or direct LLM calls
- **LLM Provider:** Groq (Llama 3.1 70B) / Gemini 1.5 Pro / Anthropic Claude
- **Vector Store:** ChromaDB
- **Embedding Model:** sentence-transformers/all-MiniLM-L6-v2
- **Language Detection:** fastText / langdetect / CLD3
- **Session Store:** Redis (production) / In-memory dict (development)
- **Authentication:** API Key header validation

### Dependencies
```bash
fastapi
uvicorn
pydantic
chromadb
sentence-transformers
langdetect
redis
httpx
python-dotenv
```

---

## 🔄 Complete Workflow

### Phase 0: System Initialization (Before First Request)

**Components Loaded:**
1. FastAPI server running on port 8000
2. ChromaDB with 100-record scam dataset embedded
3. LLM client configured (API keys set)
4. Session store initialized
5. Regex patterns loaded for intelligence extraction

**No computation happens. System waits for requests.**

---

### Phase 1: Incoming Message

**Platform sends:**
```json
POST https://your-api.com/api/message
Headers:
  x-api-key: "your-secret-key"
  Content-Type: application/json

Body:
{
  "sessionId": "abc-123",
  "message": {
    "sender": "scammer",
    "text": "CBI Officer. Money laundering case. Video call in 1 hour or arrest.",
    "timestamp": "2026-01-28T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Backend actions:**
1. Validate API key → Reject if invalid
2. Validate schema → Return 400 if malformed
3. Extract: sessionId, message text, sender, history
4. Load or create session
5. **Route decision:**
   - New session OR scam not detected → **Detection Pipeline**
   - Existing session with scam detected → **Engagement Pipeline**

---

### Phase 2: Detection Pipeline (New Sessions)

#### Step 2.1: Pre-Screening (Minimal)
**ONLY check:**
- `message == null` → IGNORE
- `message.text == null` → IGNORE
- `message.text == ""` → IGNORE
- `typeof(message.text) != string` → IGNORE
- `message.text.strip() == ""` → IGNORE

**If fails:** Return `{"reply": null, "action": "ignore"}`  
**If passes:** Continue to 2.2

---

#### Step 2.2: Language Detection
**Use:** fastText (recommended) / langdetect / CLD3

**Process:**
```python
detected_language, confidence = detect_language(message.text)
# Output: ("en", 0.95) or ("hi", 0.87) or ("ta", 0.92)
```

**Examples:**
- "Your account blocked" → `en` (0.95)
- "Aapka account block ho jayega" → `hi` (0.87) [Hinglish]
- "உங்கள் கணக்கு தடுக்கப்படும்" → `ta` (0.92) [Tamil]

---

#### Step 2.3: Language-Based Routing

**Supported Languages:** `["en", "hi"]` (English, Hindi/Hinglish)

**Routing Logic:**
```
IF language IN ["en", "hi"]:
    → NORMAL MODE (RAG + LLM)

ELSE IF language == "unknown" AND confidence < 0.6:
    → NORMAL MODE (might be English with typos)

ELSE:
    → STRICT MODE (LLM-only, tightened thresholds)
```

---

#### Step 2.4A: NORMAL MODE (English/Hinglish)

**Sub-step 1: RAG Retrieval (Evidence Gathering)**
1. Embed incoming message using sentence-transformers
2. Query ChromaDB vector database
3. Retrieve top-K=3-5 similar scam patterns
4. Extract: `id`, `category`, `scam_type`, `intent`, `similarity_score`

**Output:**
```
Match #1: Similarity: 0.92 (HIGH)
  Category: digital_arrest
  Scam Type: authority_impersonation
  Pattern: "Authority impersonates law enforcement..."

Match #2: Similarity: 0.78 (MEDIUM)
  Category: kyc_banking
  Pattern: "Bank threatens account block..."

Match #3: Similarity: 0.65 (LOW)
  Category: courier_customs
  Pattern: "Parcel seized, customs duty..."
```

**Sub-step 2: Format RAG Context for LLM**
```
Knowledge Base Matches:

Match #1 (Similarity: 0.92 - HIGH):
• Category: digital_arrest
• Scam Type: authority_impersonation
• Pattern: Authority impersonates law enforcement using urgency and threats to force immediate action

Match #2 (Similarity: 0.78 - MEDIUM):
• Category: kyc_banking
...
```

**Sub-step 3: LLM Judgment (Always, With RAG Context)**

**Prompt Structure:**
```
You are a scam detection expert for India.

INCOMING MESSAGE:
"{message_text}"

KNOWLEDGE BASE MATCHES:
{formatted_rag_context}

ANALYSIS FRAMEWORK:
1. Pattern Matching: Does it match known scam patterns?
2. Legitimacy Indicators: Official domains, toll-free numbers, transaction IDs?
3. Scam Indicators: Threats, urgency, fake domains, personal contacts?
4. Context: Could there be legitimate explanation?

RESPOND IN JSON:
{
  "is_scam": true/false,
  "confidence": 0.0-1.0,
  "primary_category": "category_name" or null,
  "reasoning": "2-3 sentence explanation",
  "matched_patterns": ["pattern1", "pattern2"],
  "red_flags": ["flag1", "flag2"],
  "legitimacy_indicators": ["indicator1"] or []
}
```

**LLM Response Example:**
```json
{
  "is_scam": true,
  "confidence": 0.92,
  "primary_category": "digital_arrest",
  "reasoning": "Message impersonates CBI officer, creates urgency with 1-hour deadline for video call, threatens arrest warrant. Uses personal phone number instead of official channel.",
  "matched_patterns": ["authority_impersonation", "urgency_tactics", "arrest_threat"],
  "red_flags": ["Personal phone: 9876543210", "1-hour deadline", "CBI impersonation", "Video call investigation"],
  "legitimacy_indicators": []
}
```

**Sub-step 4: Decision (Standard Thresholds)**
```
IF is_scam=true AND confidence ≥ 0.7:
    → ENGAGE (high confidence scam)

IF is_scam=true AND confidence 0.5-0.7:
    → PROBE (medium confidence, cautious engagement)

IF is_scam=false OR confidence < 0.5:
    → IGNORE (not a scam or too uncertain)
```

---

#### Step 2.4B: STRICT MODE (Hindi/ Tamil/Telugu/Other Languages)

**When triggered:** Unsupported languages (Hindi,Tamil, Telugu, Marathi, etc.)

**Process:**
1. **Skip RAG** (dataset is English/Hindi only)
2. **LLM-Only Detection** with modified prompt

**Strict Mode LLM Prompt:**
```
You are a scam detection expert.

INCOMING MESSAGE (Language: {detected_language}):
{message_text}

NOTE: This message is in a language outside our primary training.
Be EXTRA CAUTIOUS to avoid false positives.

STRICT REQUIREMENTS FOR MARKING AS SCAM:
• Must have MULTIPLE explicit malicious indicators
• Examples: Threats + Payment requests + Urgency + Impersonation
• If uncertain, prefer marking as NOT scam

Analyze for:
- Authority impersonation
- Payment demands
- Threats/urgency/deadlines
- Suspicious phone numbers/URLs
- Too-good-to-be-true offers

Respond in JSON: (same format as normal mode)
```

**Tightened Decision Rules (Strict Mode):**
```
IF is_scam=true AND confidence ≥ 0.85:
    → ENGAGE (higher threshold: 0.85 vs 0.7)

IF is_scam=true AND confidence 0.70-0.85:
    → PROBE (cautious middle ground)

IF is_scam=true AND confidence < 0.70:
    → IGNORE (prefer safety over engagement)

Additional: Require 3+ malicious indicators to engage
```

---

#### Step 2.5: Update Session & Store Detection Metadata

**If ENGAGE or PROBE:**
```python
session.scam_detected = True
session.detection_mode = "normal" | "strict"
session.detected_language = "en" | "hi" | "ta"
session.language_confidence = 0.87
session.category = "digital_arrest"
session.scam_type = "authority_impersonation"
session.confidence = 0.92
session.red_flags = ["Personal phone", "Arrest threat", ...]
session.reasoning = "..."
session.stage = "engagement"
session.turn_count = 1
session.extracted_intel = {}
session.start_time = timestamp
```

**If IGNORE:**
```python
session.scam_detected = False
session.status = "legitimate"
return {"reply": null, "action": "ignore"}
```

---

### Phase 3: Agent Engagement System (After Detection)

#### Step 3.1: Select Persona Based on Category

**Persona Mapping:**

| Category | Persona | Traits | Typical Response |
|----------|---------|--------|------------------|
| `digital_arrest` | scared_citizen | Panicked, fearful, compliant | "Please don't arrest me! What should I do?" |
| `job_fraud` | eager_jobseeker | Enthusiastic, hopeful | "This sounds great! What's the next step?" |
| `investment_scam` | cautious_investor | Interested but questioning | "These returns look good. How does it work?" |
| `romance_scam` | lonely_person | Friendly, open | "Nice to meet you! Tell me more" |
| `kyc_banking` | concerned_customer | Worried about account | "I don't want my account blocked!" |
| `courier_customs` | confused_receiver | Uncertain, asking | "I didn't order anything. What parcel?" |
| `lottery_prize` | excited_winner | Happy, eager | "Really? I won? How do I claim?" |
| `default` | confused_user | Uncertain | "I don't understand. Can you explain?" |

**Selected:** `scared_citizen` (for digital_arrest example)

---

#### Step 3.2: Determine Current Stage

**Stage Progression (Turn-Based):**

| Stage | Turn Range | Goal | Extraction Focus |
|-------|------------|------|------------------|
| **engagement** | 1-3 | Build trust, show interest | contact_method, basic_process |
| **probing** | 4-7 | Extract payment methods, contacts | upi_id, phone, url, bank_details |
| **extraction** | 8-12 | Get complete modus operandi | full_process, accomplices, all accounts |
| **termination** | 13+ | Graceful exit or stall tactics | - |

**Current:** Engagement (Turn 1)

---

#### Step 3.3: Extraction Targets by Category

**Category-Specific Intel Priorities:**

**digital_arrest:**
- Fake officer name
- Case number
- Video call platform/link
- Payment details (UPI/bank)
- Impersonated authority

**job_fraud:**
- Company name
- Job description
- Registration fee amount
- Payment method
- Fake website URL

**investment_scam:**
- Platform name
- Promised returns (%)
- Minimum investment
- Withdrawal process
- Referral structure

**kyc_banking:**
- Impersonated bank name
- Fake website URL
- Requested details (CVV, OTP)
- Verification method
- Contact number

**romance_scam:**
- Profile details (name, location, job)
- Relationship stage
- Money request reason
- Payment method
- Meeting plans/excuses

---

#### Step 3.4: Generate Agent Response (LLM)

**Agent Prompt Template:**
```
You are playing the role of a {persona_name} in a conversation with a scammer.

═══════════════════════════════════════════════════════════
CONTEXT:
═══════════════════════════════════════════════════════════
Scam Type: {category}
Current Stage: {stage} (Turn {turn_count})
Persona Traits: {persona_traits}

═══════════════════════════════════════════════════════════
CONVERSATION HISTORY:
═══════════════════════════════════════════════════════════
{last_5_messages}

═══════════════════════════════════════════════════════════
LATEST SCAMMER MESSAGE:
═══════════════════════════════════════════════════════════
{scammer_message}

═══════════════════════════════════════════════════════════
YOUR GOALS FOR THIS STAGE:
═══════════════════════════════════════════════════════════
{stage_goal}

Information we need to extract:
{missing_targets}

Information we already have:
{extracted_intel_summary}

═══════════════════════════════════════════════════════════
YOUR TASK:
═══════════════════════════════════════════════════════════
Generate a natural response that:
1. Stays in character (use persona traits)
2. Matches emotional tone for this scam type
3. Subtly guides toward extraction targets
4. Shows appropriate trust level for this stage
5. NEVER reveals you're testing or detecting
6. Uses natural language (can include typos/emojis if appropriate)
7. Keep short: 1-3 sentences, max 50 words

IMPORTANT RULES:
• Don't be too eager (seems suspicious)
• Don't ask for everything at once
• Let scammer lead, you follow with questions
• Show emotions appropriate to situation
• Never mention "honeypot", "testing", "AI"

RESPONSE STYLE BY STAGE:
• Engagement (1-3): Curious, concerned, basic questions
• Probing (4-7): Willing to proceed, asking for details
• Extraction (8-12): Ready to act, requesting exact steps
• Termination (13+): Stalling, excuses, delays

Generate your response as plain text:
```

**LLM Generated Response (Example):**
```
Oh no! I didn't know about any case! 😰 What is this about? 
Please don't arrest me, I haven't done anything wrong!
```

---

#### Step 3.5: Return Response to Platform

**API Response:**
```json
{
  "reply": "Oh no! I didn't know about any case! 😰 What is this about? Please don't arrest me!",
  "action": "engage",
  "metadata": {
    "scam_detected": true,
    "category": "digital_arrest",
    "confidence": 0.92,
    "stage": "engagement",
    "turn": 1
  }
}
```

**Platform displays this response to scammer.**

---

### Phase 4: Multi-Turn Engagement Loop

**Scammer sends follow-up message:**
```
"Madam, serious case. Your Aadhaar linked to ₹50 lakh transaction. 
Join Zoom video call immediately. Meeting ID: 123-456-789. 
Officer Rajesh Kumar speaking. Call: 9876543210"
```

**Platform sends request again (same sessionId):**
```json
{
  "sessionId": "abc-123",  // Same session
  "message": {
    "sender": "scammer",
    "text": "Madam, serious case. Your Aadhaar linked..."
  },
  "conversationHistory": [
    {"sender": "scammer", "text": "CBI Officer. Money laundering..."},
    {"sender": "agent", "text": "Oh no! I didn't know..."}
  ]
}
```

---

#### Step 4.1: Backend Loads Existing Session

**Session already exists with `scam_detected=true`**

**Route:** Engagement Pipeline (skip detection)

---

#### Step 4.2: Extract Intelligence (Passive)

**Scan scammer message with regex patterns:**

**Patterns:**
- UPI ID: `[\w\.\-]+@[\w]+`
- Phone: `[6-9]\d{9}`
- URL: `https?://[^\s]+`
- Bank Account: `\d{9,18}`
- IFSC: `[A-Z]{4}0[A-Z0-9]{6}`
- Case Number: `(?:Case|FIR|Ref)[\s:]*[A-Z0-9\/\-]+`

**Extracted from current message:**
- Phone: `9876543210`
- Keywords: `Zoom`, `Meeting ID: 123-456-789`, `Officer Rajesh Kumar`

**Update session:**
```python
session.extracted_intel = {
  "phone_numbers": ["9876543210"],
  "video_platform": "Zoom",
  "meeting_id": "123-456-789",
  "officer_name": "Rajesh Kumar"
}
```

---

#### Step 4.3: Update Turn Count & Stage

**Increment:** `turn_count: 1 → 2`

**Check stage:** Turn 2 still in "engagement" (turns 1-3)

---

#### Step 4.4: Generate Agent Response

**LLM Prompt (with updated context):**
```
You are: scared_citizen
Stage: engagement (Turn 2)
Conversation history: [last 5 messages]
Latest scammer message: "Madam, serious case..."

Goals: Continue showing fear, ask for details

Already extracted:
- Officer name: Rajesh Kumar
- Phone: 9876543210
- Video platform: Zoom
- Meeting ID: 123-456-789

Still need:
- UPI ID / bank account
- Payment amount
- Complete process steps

Generate response:
```

**LLM Response:**
```
This is so scary! 😨 I can join the video call sir. 
But what documents do I need? And will I need to pay any fine?
```

---

#### Step 4.5: Return Response & Continue Loop

**API Response:**
```json
{
  "reply": "This is so scary! 😨 I can join the video call sir. But what documents do I need?",
  "action": "continue",
  "turn_count": 2,
  "extracted_intel_count": 4
}
```

**This loop continues for each scammer message until stop condition...**

---

### Phase 5: Intelligence Extraction (Throughout Conversation)

**Passive Extraction Every Turn:**

**Regex Patterns Applied:**
1. **UPI IDs:** `scammer@paytm`, `fraud@ybl`
2. **Phone Numbers:** `9876543210`, `+91-9988776655`
3. **URLs:** `fake-bank.com`, `bit.ly/xyz`, `scam.gov.co`
4. **Bank Accounts:** `1234567890123456`
5. **IFSC Codes:** `HDFC0001234`
6. **Case Numbers:** `CBI/ML/2847/2024`

**Stored Incrementally:**
```python
session.extracted_intel = {
  "upi_ids": ["scammer@paytm"],
  "phone_numbers": ["9876543210", "+91-9988776655"],
  "urls": ["fake-cbi-portal.gov.co"],
  "bank_accounts": [],
  "ifsc_codes": [],
  "case_numbers": ["CBI/ML/2847/2024"],
  "video_platforms": ["Zoom"],
  "meeting_ids": ["123-456-789"],
  "officer_names": ["Rajesh Kumar"],
  "impersonated_authorities": ["CBI"],
  "keywords": ["money laundering", "arrest warrant", "video call", "urgent"]
}
```

**No active probing** - agent stays natural, scammer volunteers information

---

### Phase 6: Stop Condition Check

**After Every Turn, Check:**

1. **Intelligence Objectives Met**
   - Critical intel extracted (UPI/phone/URL/process)
   - Turn count ≥ 8
   - All category-specific targets obtained

2. **Maximum Turns Reached**
   - Turn count ≥ 15-20
   - Conversation too long

3. **Scammer Disengages**
   - Scammer stops replying
   - Scammer becomes suspicious
   - Conversation goes off-track

4. **Manual Override** (if implemented)
   - Admin triggers stop

**If any condition met → Proceed to Phase 7**

---

### Phase 7: Session Finalization

#### Step 7.1: Mark Session Complete
```python
session.status = "complete"
session.end_time = current_timestamp
session.total_turns = 18
session.duration_seconds = 2700  # 45 minutes
```

---

#### Step 7.2: Assemble Final Intelligence Report

**Consolidate all extracted data:**
```json
{
  "sessionId": "abc-123",
  "scamDetected": true,
  "scamCategory": "digital_arrest",
  "scamType": "authority_impersonation",
  "detectionConfidence": 0.92,
  "detectionMode": "normal",
  "detectedLanguage": "en",
  
  "totalMessagesExchanged": 18,
  "conversationDurationSeconds": 2700,
  
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["fake-cbi-portal.gov.co"],
    "phoneNumbers": ["+91-9876543210", "+91-9988776655"],
    "suspiciousKeywords": ["money laundering", "arrest warrant", "urgent", "video call", "case number"],
    "videoCallPlatforms": ["Zoom"],
    "meetingIds": ["123-456-789"],
    "caseNumbers": ["CBI/ML/2847/2024"],
    "impersonatedAuthorities": ["CBI"],
    "fakeOfficerNames": ["Rajesh Kumar", "Inspector Sharma"]
  },
  
  "conversationAnalysis": {
    "redFlags": [
      "Personal phone number used as official contact",
      "Fake government domain (.gov.co instead of .gov.in)",
      "1-hour deadline creating urgency",
      "Video call investigation (not legal procedure)",
      "Payment demand via UPI",
      "Multiple threatening language"
    ],
    "tacticsUsed": [
      "Authority impersonation (CBI)",
      "Fear and panic creation",
      "Urgency tactics with tight deadline",
      "Legal threat (arrest warrant)",
      "Isolation attempt (video call)",
      "Payment extraction (UPI)"
    ],
    "personaUsed": "scared_citizen",
    "stagesCompleted": ["engagement", "probing", "extraction"]
  },
  
  "agentNotes": "Scammer impersonated CBI officer claiming victim's Aadhaar linked to money laundering case worth ₹50 lakh. Used fear tactics with 1-hour deadline for arrest. Attempted to conduct fake investigation via Zoom video call. Requested payment of ₹25,000 as security deposit via UPI ID scammer@paytm. Provided fake case number CBI/ML/2847/2024 and impersonated Officer Rajesh Kumar. Agent successfully maintained scared_citizen persona throughout 18-turn conversation, extracting complete modus operandi including payment method, contact details, video call setup, and full scam process without revealing detection."
}
```

---

### Phase 8: Mandatory GUVI Callback

**⚠️ CRITICAL - Required for Evaluation**

**API Call:**
```
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult

Headers:
  x-api-key: YOUR_TEAM_API_KEY
  Content-Type: application/json

Body:
{
  "sessionId": "abc-123",
  "scamDetected": true,
  "totalMessagesExchanged": 18,
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["fake-cbi-portal.gov.co"],
    "phoneNumbers": ["+91-9876543210"],
    "suspiciousKeywords": ["money laundering", "arrest", "urgent"]
  },
  "agentNotes": "Digital arrest scam. Impersonated CBI officer. Extracted UPI ID, phone numbers, fake website, and complete modus operandi over 18 exchanges."
}
```

**Response Expected:**
```json
{
  "status": "success",
  "message": "Intelligence report received",
  "sessionId": "abc-123"
}
```

**If this callback is NOT made → Your solution will NOT be evaluated!**

---

### Phase 9: Session Closure

#### Step 9.1: Archive Session Data
- Save complete conversation history to database
- Store intelligence report for analytics
- Log detection metadata for review
- Generate session summary

#### Step 9.2: Clear Active Session
- Remove from Redis/in-memory active sessions
- Free up resources
- Mark as archived

#### Step 9.3: Agent Stops Replying
- No more responses for this sessionId
- If platform sends more messages:
  ```json
  {
    "reply": null,
    "action": "session_ended",
    "message": "Engagement complete. Session closed."
  }
  ```

---

## 🚀 Deployment Checklist

### Pre-Deployment

- [ ] All environment variables set (API keys, Redis URL)
- [ ] Dataset loaded into ChromaDB
- [ ] LLM client configured and tested
- [ ] GUVI callback endpoint tested
- [ ] API authentication tested
- [ ] Session management working
- [ ] Intelligence extraction verified

### Environment Variables

Create `.env` file:
```bash
# API Configuration
API_KEY=your-secret-api-key
PORT=8000
HOST=0.0.0.0

# LLM Provider
LLM_PROVIDER=groq  # or gemini or anthropic
LLM_API_KEY=your-llm-api-key
LLM_MODEL=llama-3.1-70b-versatile

# Vector Store
CHROMA_DB_PATH=./chroma_db

# Session Store
REDIS_URL=redis://localhost:6379/0
SESSION_TIMEOUT=3600  # 1 hour

# GUVI Integration
GUVI_API_KEY=your-guvi-team-key
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult

# Logging
LOG_LEVEL=INFO
LOG_FILE=honeypot.log
```

### Cloud Deployment (Render / Vercel)

#### Backend Deployment (Render)

The FastAPI backend is deployed using **Render**.

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

Render automatically assigns PORT=10000.

**Environment Variables:**
Set all required variables in the Render dashboard (API_KEY, LLM keys, Redis URL, GUVI callback config, etc.).

**After deployment, Render provides a public API URL:**

https://your-backend-name.onrender.com

#### Frontend Deployment (Vercel – Optional)

If a frontend UI is used, it can be deployed on Vercel.

**Steps:**

```bash
npm install
npm run build
```

**Deploy the repository via the Vercel dashboard and configure the backend API URL as an environment variable.**

**Build and Run:**
```bash
docker build -t honeypot-api .
docker run -d -p 8000:8000 --env-file .env honeypot-api
```

### Production Deployment

**Using Uvicorn:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Using Gunicorn:**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Monitoring

**Health Check Endpoint:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

**Metrics to Track:**
- Total requests processed
- Detection accuracy (scam vs legitimate)
- Average response time
- Intelligence extraction rate
- GUVI callback success rate
- Error rate

---

## ⚖️ Ethical Guidelines

### Do's ✅

- ✅ Detect scam intent accurately
- ✅ Engage scammers to extract intelligence
- ✅ Protect potential victims by gathering scam tactics
- ✅ Report findings to authorities (via GUVI callback)
- ✅ Maintain natural conversational flow
- ✅ Log all interactions for analysis

### Don'ts ❌

- ❌ **No real person impersonation** - Don't pretend to be specific individuals
- ❌ **No illegal instructions** - Don't suggest or assist illegal activities
- ❌ **No harassment** - Don't threaten or abuse scammers
- ❌ **No payment execution** - Don't actually send money
- ❌ **No personal data storage** - Don't store sensitive user information
- ❌ **No vigilante actions** - Only report to authorities

