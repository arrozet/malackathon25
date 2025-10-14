# FastAPI + Oracle python-oracledb (thin mode) Dockerfile
# Configured for Oracle Cloud Autonomous Database with wallet
FROM python:3.12-slim AS base

# Metadata
LABEL maintainer="Malackathon 2025 Team"
LABEL description="FastAPI application with Oracle Autonomous Database"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    TNS_ADMIN=/app/oracle_wallet

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies separately for layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source
COPY app ./app

# Copy wallet (contains certificates and connection config)
COPY app/oracle_wallet ./oracle_wallet

# Verify wallet files exist
RUN ls -la ./oracle_wallet/ && \
    test -f ./oracle_wallet/cwallet.sso && \
    test -f ./oracle_wallet/tnsnames.ora && \
    test -f ./oracle_wallet/sqlnet.ora && \
    echo "✓ Wallet files verified"

# Set wallet permissions (only readable by owner)
RUN chmod 600 ./oracle_wallet/cwallet.sso && \
    chmod 600 ./oracle_wallet/ewallet.p12 2>/dev/null || true && \
    chmod 644 ./oracle_wallet/*.ora

# Copy scripts
COPY scripts ./scripts

# Non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
