from fastapi import FastAPI
from app.api.routes import message, health
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)

# Include routers
app.include_router(message.router, prefix="/api", tags=["Message"])
app.include_router(health.router, prefix="/api", tags=["System"])

@app.get("/")
async def root():
    return {"message": "Honey-Pot API is active", "status": "online"}
