# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile — E-Commerce WhatsApp Bot
# ─────────────────────────────────────────────────────────────────────────────
# Build:   docker build -t ecommerce-bot .
# Run:     docker run -p 5000:5000 --env-file .env ecommerce-bot
#
# Uses a two-stage build:
#   Stage 1 (builder) — installs Python deps in an isolated layer
#   Stage 2 (runtime) — copies only what's needed for a lean final image
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# System deps needed to compile some Python packages (e.g. psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy requirements first — Docker caches this layer if requirements.txt
# hasn't changed, making rebuilds much faster.
COPY requirements.txt .

# Install into a local prefix so we can copy just the packages in stage 2
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Runtime system deps (libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Create writable directories the app needs at runtime
RUN mkdir -p instance backups logs \
    && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the port gunicorn will listen on
EXPOSE 5000

# Environment defaults (override via --env-file or -e flags)
ENV FLASK_ENV=production \
    PORT=5000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Healthcheck — Docker will mark the container unhealthy if / stops responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" \
    || exit 1

# Run database migrations + start gunicorn
# Using exec form (JSON array) so signals are passed correctly to gunicorn
CMD ["sh", "-c", \
     "flask init-db && flask seed-db && \
      gunicorn wsgi:app \
        --bind 0.0.0.0:${PORT} \
        --workers 2 \
        --timeout 60 \
        --access-logfile - \
        --error-logfile -"]