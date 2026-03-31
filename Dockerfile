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

# Start the ADK API server serving the weather_agent package
CMD ["adk", "api_server", "--port", "8080", "weather_agent"]
