FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr (important for Cloud Run logs)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run expects port 8080
EXPOSE 8080

# adk api_server AGENTS_DIR expects the parent directory containing agent folders.
# --host 0.0.0.0 is required for Cloud Run (default is 127.0.0.1).
CMD ["adk", "api_server", "--host", "0.0.0.0", "--port", "8080", "."]
