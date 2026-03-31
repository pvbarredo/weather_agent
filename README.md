# Weather Agent — ADK + MCP + Cloud Run

An AI-powered weather assistant built with **Google ADK** (Agent Development Kit) that uses the **Model Context Protocol (MCP)** to connect to a custom weather data server. Deployed as a single container on **Google Cloud Run**.

## Architecture

```
User ──► Cloud Run (ADK API Server, port 8080)
              │
              ▼
         ADK Agent (Gemini 2.0 Flash)
              │  MCP (stdio)
              ▼
         MCP Weather Server (subprocess)
              │  HTTP
              ▼
         Open-Meteo API (free, no key)
```

- **ADK Agent** (`weather_agent/agent.py`) — conversational agent powered by Gemini 2.0 Flash. Connects to the MCP server via `MCPToolset` with stdio transport.
- **MCP Weather Server** (`mcp_weather_server/server.py`) — exposes two tools (`get_current_weather`, `get_weather_forecast`) using the `FastMCP` framework. Calls the free Open-Meteo API for geocoding and weather data.
- **Single container** — the ADK agent spawns the MCP server as a child process; no separate services needed.

## Tools

| Tool | Description |
|------|-------------|
| `get_current_weather(city)` | Returns current temperature, humidity, wind speed, and conditions |
| `get_weather_forecast(city, days)` | Returns a multi-day forecast (1–7 days) with high/low temps and precipitation |

## Prerequisites

- Python 3.12+
- A [Google AI Studio](https://aistudio.google.com/) API key (for Gemini)
- Docker (for containerised deployment)
- `gcloud` CLI (for Cloud Run deployment)

## Local Setup

```bash
# 1. Clone and enter the repository
cd track2-challenge

# 2. Create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Gemini API key
cp .env.example .env
# Edit .env and add your real GOOGLE_API_KEY

# 5. Run the agent locally (web UI)
adk web weather_agent
```

Open the URL printed in the terminal (usually `http://localhost:8000`) and ask:
> "What's the weather in Tokyo?"

## Docker (Local)

```bash
docker build -t weather-agent .
docker run -p 8080:8080 -e GOOGLE_API_KEY=your-key-here weather-agent
```

## Deploy to Cloud Run

```bash
# Set your project
export PROJECT_ID=your-gcp-project-id

# Build the image
gcloud builds submit --tag gcr.io/$PROJECT_ID/weather-agent

# Deploy
gcloud run deploy weather-agent \
  --image gcr.io/$PROJECT_ID/weather-agent \
  --port 8080 \
  --set-env-vars GOOGLE_API_KEY=your-key-here \
  --allow-unauthenticated \
  --region us-central1
```

The command will print the Cloud Run URL. Use that URL to interact with the agent.

## Project Structure

```
track2-challenge/
├── weather_agent/
│   ├── __init__.py      # Package init
│   └── agent.py         # ADK root_agent with MCPToolset
├── mcp_weather_server/
│   ├── __init__.py      # Package init
│   └── server.py        # FastMCP server with weather tools
├── requirements.txt     # Python dependencies
├── Dockerfile           # Cloud Run container image
├── .env.example         # API key template
└── README.md            # This file
```

## License

MIT
