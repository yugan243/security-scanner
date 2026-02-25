# ============================================================
# Vigil — AI-Powered Security Scanner
# Multi-stage Docker build for a lean production image
# ============================================================

# Stage 1: Builder — install Python dependencies via Poetry
# Poetry is ~300MB and only needed for installing deps,
# so we discard it after this stage.
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files first (Docker layer caching)
# If dependencies haven't changed, this layer is cached
COPY pyproject.toml poetry.lock* ./

# Install dependencies into the system Python (no virtualenv)
RUN poetry config virtualenvs.create false && \
    poetry install --no-root


# ============================================================
# Stage 2: Runtime — lean production image
# Only contains: Python + git + semgrep + deps + source code
# ============================================================
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
# - git: needed to clone remote repositories
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install Semgrep (the static analysis engine)
RUN pip install --no-cache-dir semgrep

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code (only vigil/, not tests or dev files)
COPY vigil/ ./vigil/

# Signal that we're running inside Docker
# This tells the CLI to show a help message instead of
# trying to run the interactive setup wizard
ENV VIGIL_DOCKER=1

# Entry point — all arguments are passed to the Vigil CLI
# Usage: docker run vigil scan https://github.com/some/repo
ENTRYPOINT ["python", "-m", "vigil.main"]
