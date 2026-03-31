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

# Use the Python entrypoint for reliable Cloud Run startup
# (reads PORT env var, binds to 0.0.0.0)
CMD ["python", "main.py"]
