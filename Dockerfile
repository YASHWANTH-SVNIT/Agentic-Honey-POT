# Python 3.11 Runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Port for Hugging Face Spaces (7860 is standard)
    PORT=7860 \
    # Helper to fix caching issues
    PIP_NO_CACHE_DIR=1

# Install system dependencies (gcc/g++ often needed for some python libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create a user to run the app (security best practice)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Copy application code
COPY --chown=user . .

# Pre-download the embedding model to the image (Speeds up startup!)
# We run a tiny script to trigger the download
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" || true

# Expose the port
EXPOSE 7860

# Startup command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
