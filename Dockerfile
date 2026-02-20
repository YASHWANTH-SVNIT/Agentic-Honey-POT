# Python 3.11 Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    PIP_NO_CACHE_DIR=1 \
    TRANSFORMERS_CACHE=/app/.cache/transformers \
    HF_HOME=/app/.cache/huggingface

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Setup application directory
WORKDIR /app

# Copy and install Python dependencies early (better layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directories (models will download on first run)
RUN mkdir -p /app/.cache/transformers /app/.cache/huggingface /app/chroma_db

# Create non-root user
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

# Switch to non-root user for runtime
USER user

# Expose port
EXPOSE 7860

# Start application (models download on first startup)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
