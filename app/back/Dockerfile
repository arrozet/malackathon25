# Backend Dockerfile - FastAPI + Oracle Autonomous Database
FROM python:3.12-slim

# Metadata
LABEL maintainer="Malackathon 2025 Team"
LABEL description="FastAPI Backend with Oracle Autonomous Database"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    TNS_ADMIN=/app/oracle_wallet

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
# El contexto del build es la raíz del proyecto
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory to maintain import structure
COPY app ./app

# Copy Oracle wallet
COPY app/oracle_wallet ./oracle_wallet

# Verify wallet files
RUN ls -la ./oracle_wallet/ && \
    test -f ./oracle_wallet/cwallet.sso && \
    test -f ./oracle_wallet/tnsnames.ora && \
    echo "✓ Wallet files verified"

# Set proper permissions
RUN chmod 600 ./oracle_wallet/cwallet.sso && \
    chmod 644 ./oracle_wallet/*.ora

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.back.main:app", "--host", "0.0.0.0", "--port", "8000"]
