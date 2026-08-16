# ---------- Builder Stage ----------
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system dependencies (only if required by Python packages)
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (Docker cache)
COPY requirements.txt .

# Install Python dependencies into a separate location
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Runtime Stage ----------
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from builder into lowercase /usr/local
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Ensure appuser owns the directory before dropping root privileges
RUN useradd -m ticketdesk && chown -R ticketdesk:ticketdesk /app

USER ticketdesk

# FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]