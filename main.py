"""
Agentic Honey-Pot API - Production Ready
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import settings
from app.api.routes import message, health

app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered scam detection and engagement",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(message.router, prefix="/api", tags=["Message"])

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("AGENTIC HONEY-POT API - STARTING")
    print("=" * 60)
    print(f"Provider: {settings.LLM_PROVIDER}")
    print(f"Threshold: {settings.DETECTION_THRESHOLD}")
    print("=" * 60)
    
    # Pre-load vector store
    try:
        from app.services.rag.vector_store import get_vector_store
        vs = get_vector_store()
        if vs.collection.count() == 0:
            vs.load_dataset_from_json()
    except Exception as e:
        print(f"[Startup] Vector store: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=False)