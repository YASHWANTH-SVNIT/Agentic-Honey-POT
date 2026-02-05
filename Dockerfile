# Python 3.11 Runtime
FROM python:3.11-slim

# Create a user to run the app (security best practice for HF Spaces)
RUN useradd -m -u 1000 user

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY --chown=user requirements.txt .

# Install dependencies (as user!)
USER user
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY --chown=user . .

# Ensure chroma_db directory exists and is writable
RUN mkdir -p /app/chroma_db

# Pre-download the embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" || true

# Expose the port
EXPOSE 7860

# Startup command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
