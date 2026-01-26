Project: Agentic Honey-Pot for Scam Detection & Intelligence Extraction 

# 1. Project Overview

Objective: Build an AI-powered system that detects scam intent and autonomously engages scammers to extract intelligence without revealing detection.


Core Function: Deploy a public REST API that accepts message events and returns structured JSON responses.

# 2. Technical Stack

Framework: FastAPI.

Agentic Logic: LangGraph.


LLM Engine: Groq / Gemini 1.5 Pro.

Vector Store: ChromaDB.

Authentication: API Key Header (x-api-key).

# 3. Development Phases

## Phase 1: API Infrastructure & Schemas

Authentication: Secure all endpoints using x-api-key: YOUR_SECRET_API_KEY.


Request Handler: Create an endpoint to accept sessionId, message, conversationHistory, and metadata.


Data Fields: Define Pydantic models for sender (scammer/user), text, and timestamp .


Response Model: Structure output to include status, scamDetected, and engagementMetrics .

## Phase 2: Scam Detection Node

Intent Analysis: Build a classifier to identify bank fraud, UPI fraud, phishing, and fake offers.


Initial Evaluation: Process the first incoming message to trigger the AI Agent if scam intent is detected .

## Phase 3: Agentic Engagement (LangGraph)

Persona Module: Design and maintain a believable human-like persona throughout the interaction.


Conversation Loop: Handle multi-turn, dynamic responses while avoiding detection exposure.


Self-Correction: Implement an agent node for real-time response adjustment and behavioral adaptation.

## Phase 4: Intelligence Extraction

Data Parsing: Automate the extraction of bankAccounts, upilds, phishingLinks, and phoneNumbers .


Contextual Insights: Identify suspiciousKeywords and generate agentNotes on scammer tactics .


Metric Tracking: Calculate totalMessagesExchanged and engagementDurationSeconds .

## Phase 5: Final Evaluation Callback

Termination Logic: Confirm intelligence extraction is finished and engagement has reached a sufficient depth .


Mandatory Reporting: Send a POST request with the final JSON payload to https://hackathon.guvi.in/api/updateHoneyPotFinalResult.


Payload Components: Include the sessionId, scamDetected flag, and the full extractedIntelligence dictionary .

# 4. Operational Constraints & Ethics

Evaluation Criteria: Solutions are graded on detection accuracy, agent engagement quality, and API stability.


Ethical Guardrails: No impersonation of real individuals, no illegal instructions, and no harassment .