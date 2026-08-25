# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ─── Dependencies layer ───────────────────────
FROM base AS dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─── Development / Production image ──────────
FROM dependencies AS runtime
COPY . .

# Create reports directory
RUN mkdir -p /app/reports

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --group appuser
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
