"""ADK Weather Agent — uses MCP to call weather tools and respond with Gemini."""

import os
import sys

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp.client.stdio import StdioServerParameters

# Resolve the path to the MCP server module so it works from any working directory
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

root_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    instruction="""You are a friendly and knowledgeable weather assistant.

Your capabilities:
- Get current weather conditions for any city worldwide.
- Get multi-day weather forecasts (up to 7 days) for any city.

Guidelines:
- If the user does not specify a city, politely ask them which city they want weather for.
- Always present temperatures in Celsius with the unit clearly shown.
- Include wind speed, humidity, and weather condition in your current weather responses.
- For forecasts, present the data in a clear, day-by-day format.
- If a city cannot be found, let the user know and suggest they check the spelling.
- Be concise but informative. Use a conversational tone.
- When presenting weather data, make it easy to read — use bullet points or short paragraphs.
""",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "mcp_weather_server.server"],
                    env={**os.environ, "PYTHONPATH": _PROJECT_ROOT},
                ),
            ),
        )
    ],
)
