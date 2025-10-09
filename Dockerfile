# N8N Workflow Scraper - Dockerfile
# Version: 2.0
# Python: 3.11 (slim for smaller image size)

FROM python:3.11-slim

# ============================================================================
# METADATA
# ============================================================================
LABEL maintainer="path58-rnd"
LABEL version="2.0"
LABEL description="N8N Workflow Dataset Scraper"

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# ============================================================================
# INSTALL SYSTEM DEPENDENCIES
# ============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    # Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-eng \
    # Utilities
    wget \
    ca-certificates \
    fonts-liberation \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ============================================================================
# CREATE APP USER (Security best practice)
# ============================================================================
RUN useradd -m -u 1000 scraper && \
    mkdir -p /app /data /media && \
    chown -R scraper:scraper /app /data /media

# ============================================================================
# SET WORKING DIRECTORY
# ============================================================================
WORKDIR /app

# ============================================================================
# INSTALL PYTHON DEPENDENCIES
# ============================================================================
# Copy requirements first (better caching)
COPY --chown=scraper:scraper requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only)
RUN playwright install chromium && \
    playwright install-deps chromium

# ============================================================================
# COPY APPLICATION CODE
# ============================================================================
COPY --chown=scraper:scraper . .

# ============================================================================
# CREATE DATA DIRECTORIES
# ============================================================================
RUN mkdir -p \
    /data/raw \
    /data/processed \
    /data/exports \
    /media/images \
    /media/videos \
    /app/logs && \
    chown -R scraper:scraper /data /media /app/logs

# ============================================================================
# SWITCH TO NON-ROOT USER
# ============================================================================
USER scraper

# ============================================================================
# HEALTHCHECK
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# ============================================================================
# VOLUME MOUNTS (for persistence)
# ============================================================================
VOLUME ["/data", "/media", "/app/logs"]

# ============================================================================
# ENTRY POINT
# ============================================================================
ENTRYPOINT ["python"]
CMD ["scripts/scrape.py", "--help"]

# ============================================================================
# BUILD INSTRUCTIONS
# ============================================================================
# docker build -t n8n-scraper:2.0 .
# docker run -v $(pwd)/data:/data -v $(pwd)/media:/media n8n-scraper:2.0 scripts/scrape.py
# ============================================================================