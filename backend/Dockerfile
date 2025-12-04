# ============ STAGE 1: BUILDER ============
FROM python:3.11-slim AS builder

WORKDIR /build

# Install BUILD dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    git \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# GitHub token
ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=${GITHUB_TOKEN}
RUN git config --global url."https://oauth2:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"

# Clone config
RUN git clone https://github.com/lunch-corp/yamyam-lab-config.git /build/config

# Install uv
RUN pip install --no-cache-dir uv

# Install Python dependencies
COPY pyproject.toml .
RUN uv pip install --system --no-cache -e .

# ============ STAGE 2: RUNTIME ============
FROM python:3.11-slim

WORKDIR /app

# Install RUNTIME dependencies only (not build tools)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libpq5 \
    curl \
    sshpass \
    openssh-client \
    libgfortran5 \
    libomp5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy config (without .git)
COPY --from=builder /build/config /app/config
RUN rm -rf /app/config/.git

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers $WORKERS"]
