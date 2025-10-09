# N8N Workflow Scraper - Production Dockerfile
# Version: 1.0
# Python: 3.11

FROM python:3.11-slim

# Metadata
LABEL maintainer="RND Team"
LABEL project="n8n-workflow-scraper"
LABEL version="1.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Tesseract for OCR
    tesseract-ocr \
    libtesseract-dev \
    # System libraries
    wget \
    gnupg \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and dependencies
# Note: Using --with-deps for automatic dependency installation
RUN playwright install --with-deps chromium || \
    (playwright install chromium && echo "Playwright installed without system deps")

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed data/exports logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///data/workflows.db
ENV LOG_LEVEL=INFO

# Initialize database
RUN python scripts/setup_db.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; from src.database.schema import get_session; session = get_session(); session.close(); sys.exit(0)" || exit 1

# Default command
CMD ["pytest", "tests/", "-v"]

