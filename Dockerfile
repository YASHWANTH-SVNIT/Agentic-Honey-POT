# Python 3.11 Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Standard HF Spaces port
    PORT=7860 \
    # Fix caching issues
    PIP_NO_CACHE_DIR=1

# 1. Install System Dependencies (as ROOT)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python Dependencies (as ROOT - avoids permission issues)
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Setup Application (still as ROOT)
COPY . .

# 4. Create User and Fix Permissions (CRITICAL STEP)
# Create a user with ID 1000
RUN useradd -m -u 1000 user
# Create the ChromaDB directory explicitly
RUN mkdir -p /app/chroma_db
# Give USER ownership of the entire application directory
RUN chown -R user:user /app

# 5. Pre-download Embedding Model (as ROOT is fine, it goes to cache)
# But better to do it as user so they can read it, or set cache dir. 
# We'll just run it; usually cache is readable.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" || true

# 6. Switch to User for Runtime
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Expose port
EXPOSE 7860

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
