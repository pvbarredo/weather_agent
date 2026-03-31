"""MCP Weather Server — exposes weather tools via the Model Context Protocol.

Uses the free Open-Meteo API (no API key required) for geocoding and forecasts.
Designed to run over stdio transport so the ADK agent can spawn it as a subprocess.
"""

import json
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="weather",
    instructions="Provides current weather and multi-day forecasts for any city worldwide.",
)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Map WMO weather codes to human-readable descriptions
WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


async def _geocode(city: str) -> dict[str, Any]:
    """Resolve a city name to latitude, longitude, and display name."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(GEOCODING_URL, params={"name": city, "count": 1, "language": "en", "format": "json"})
        resp.raise_for_status()
        data = resp.json()

    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"City not found: {city}")

    loc = data["results"][0]
    return {
        "name": loc.get("name", city),
        "country": loc.get("country", ""),
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
    }


@mcp.tool()
async def get_current_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: Name of the city (e.g. "Tokyo", "New York", "London").

    Returns:
        A JSON string with current temperature, wind speed, humidity,
        and weather condition.
    """
    location = await _geocode(city)

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    current = data["current"]
    weather_code = current.get("weather_code", -1)

    result = {
        "location": f"{location['name']}, {location['country']}",
        "temperature_celsius": current["temperature_2m"],
        "apparent_temperature_celsius": current["apparent_temperature"],
        "humidity_percent": current["relative_humidity_2m"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "condition": WMO_CODES.get(weather_code, "Unknown"),
        "observation_time": current.get("time", ""),
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_weather_forecast(city: str, days: int = 3) -> str:
    """Get a multi-day weather forecast for a city.

    Args:
        city: Name of the city (e.g. "Tokyo", "New York", "London").
        days: Number of forecast days (1–7, default 3).

    Returns:
        A JSON string with daily high/low temperatures, precipitation,
        and weather conditions for the requested number of days.
    """
    days = max(1, min(days, 7))
    location = await _geocode(city)

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
        "temperature_unit": "celsius",
        "forecast_days": days,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data["daily"]
    forecast_days = []
    for i in range(len(daily["time"])):
        weather_code = daily["weather_code"][i]
        forecast_days.append({
            "date": daily["time"][i],
            "high_celsius": daily["temperature_2m_max"][i],
            "low_celsius": daily["temperature_2m_min"][i],
            "precipitation_mm": daily["precipitation_sum"][i],
            "condition": WMO_CODES.get(weather_code, "Unknown"),
        })

    result = {
        "location": f"{location['name']}, {location['country']}",
        "forecast": forecast_days,
    }
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
