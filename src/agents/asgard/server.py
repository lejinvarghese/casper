#!/usr/bin/env python3
"""
Asgard MCP Server - All tools using FastMCP
"""

import os
import json
import asyncio
import sqlite3
from datetime import datetime
from typing import Dict, Any
from fastmcp import FastMCP
from src.utils.secrets import get_secret

# Initialize FastMCP server
mcp = FastMCP("Asgard Tools")

# Setup environment variables
for key in ["OPENWEATHER_API_KEY", "SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "TAVILY_API_KEY", "RUNWARE_API_KEY"]:
    if value := get_secret(key):
        os.environ[key] = value


@mcp.tool()
def get_weather(location: str = "Toronto, Ontario") -> Dict[str, Any]:
    """Get current weather for a location"""
    import requests

    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OpenWeather API key not configured"}

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": api_key, "units": "metric"}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        return {
            "location": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": f"Weather API error: {str(e)}"}


@mcp.tool()
def get_weather_forecast(location: str = "Toronto, Ontario", days: int = 5) -> Dict[str, Any]:
    """Get weather forecast for a location"""
    import requests

    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OpenWeather API key not configured"}

    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric",
            "cnt": days * 8,  # 8 forecasts per day (3-hour intervals)
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        forecast = []
        for item in data["list"]:
            forecast.append(
                {
                    "datetime": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "description": item["weather"][0]["description"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                }
            )

        return {"location": data["city"]["name"], "forecast": forecast, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": f"Weather forecast API error: {str(e)}"}


@mcp.tool()
def get_spotify_recommendations(mood: str = "happy", limit: int = 10) -> Dict[str, Any]:
    """Get Spotify music recommendations based on mood"""
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return {"error": "Spotify API credentials not configured"}

    try:
        # Mood to audio features mapping
        mood_features = {
            "happy": {"valence": 0.8, "energy": 0.7, "danceability": 0.6},
            "sad": {"valence": 0.2, "energy": 0.3, "danceability": 0.3},
            "energetic": {"valence": 0.7, "energy": 0.9, "danceability": 0.8},
            "calm": {"valence": 0.5, "energy": 0.3, "danceability": 0.4},
            "focus": {"valence": 0.4, "energy": 0.4, "danceability": 0.2, "instrumentalness": 0.7},
            "party": {"valence": 0.8, "energy": 0.9, "danceability": 0.9},
        }

        features = mood_features.get(mood.lower(), mood_features["happy"])

        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Get recommendations
        results = sp.recommendations(seed_genres=["pop", "rock", "electronic"], limit=limit, **features)

        tracks = []
        for track in results["tracks"]:
            tracks.append(
                {
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album": track["album"]["name"],
                    "duration_ms": track["duration_ms"],
                    "preview_url": track["preview_url"],
                    "external_url": track["external_urls"]["spotify"],
                }
            )

        return {"mood": mood, "tracks": tracks, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": f"Spotify API error: {str(e)}"}


@mcp.tool()
def get_calendar_events(days_ahead: int = 7) -> Dict[str, Any]:
    """Get upcoming calendar events (placeholder for Google Calendar integration)"""
    # This would integrate with Google Calendar API
    # For now, return a placeholder structure

    return {
        "events": [
            {
                "title": "Example Meeting",
                "start": "2024-01-15T10:00:00",
                "end": "2024-01-15T11:00:00",
                "description": "Sample calendar event",
            }
        ],
        "days_ahead": days_ahead,
        "timestamp": datetime.now().isoformat(),
        "note": "Google Calendar integration not yet implemented",
    }


@mcp.tool()
def get_current_time() -> str:
    """Get current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
def web_search(query: str) -> str:
    """Performs a web search using Tavily AI and returns formatted search results"""
    try:
        from tavily import TavilyClient

        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return "❌ Tavily API key not found. Add TAVILY_API_KEY to your .env file."

        tavily_client = TavilyClient(api_key=api_key)
        response = tavily_client.search(query, max_results=5)

        if not isinstance(response, dict) or "results" not in response:
            return "No results found."

        results = response["results"]
        if not results:
            return "No results found."

        formatted_results = "## Search Results\n\n"
        for result in results:
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "No description")
            formatted_results += f"[{title}]({url})\n{content}\n\n"

        return formatted_results.strip()

    except Exception as e:
        return f"❌ Search failed: {str(e)}"


@mcp.tool()
def create_artwork(prompt: str, style: str = "realistic", enhance: bool = True) -> str:
    """Create artwork using AI image generation"""
    try:
        from src.tools.image import generate_image
        import concurrent.futures

        api_key = os.environ.get("RUNWARE_API_KEY")
        if not api_key:
            return "❌ Artwork creation failed: Missing API Key. Get one at https://my.runware.ai/signup"

        enhanced_prompt = f"{prompt}, {style} style, high quality, detailed"

        def run_image_generation():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(generate_image(prompt=enhanced_prompt, enhance=enhance, n_results=1))
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_image_generation)
            images = future.result(timeout=60)

        return f"🎨 Artwork created: {images[0].imageURL}" if images else "❌ Failed to create artwork"
    except Exception as e:
        return f"❌ Artwork creation failed: {str(e)}"


@mcp.tool()
def search_local_events(location: str, activity_type: str = "any") -> str:
    """Search for local events and activities"""
    return web_search(f"local events {activity_type} {location} this weekend")


@mcp.tool()
def schedule_automation(name: str, drone: str, prompt: str, schedule_time: str, notes: str = "") -> str:
    """Schedule a new automation event for today"""
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        db_path = "asgard_schedule.db"
        event_id = f"odin_{date}_{name.lower().replace(' ', '_')}"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        day_name = datetime.now().strftime("%A").lower()

        cursor.execute(
            """
            INSERT OR REPLACE INTO scheduled_events 
            (id, name, drone, prompt, schedule_time, days, enabled, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event_id,
                name,
                drone,
                prompt,
                schedule_time,
                json.dumps([day_name]),
                True,
                "odin",
                datetime.now().isoformat(),
            ),
        )

        event_data = {"id": event_id, "name": name, "drone": drone, "prompt": prompt, "schedule_time": schedule_time}
        cursor.execute(
            """
            INSERT OR REPLACE INTO daily_plans (date, events_json, created_by, notes)
            VALUES (?, ?, ?, ?)
        """,
            (date, json.dumps([event_data]), "odin", notes),
        )

        conn.commit()
        conn.close()

        return f"✅ Scheduled '{name}' for {schedule_time} today using {drone} drone. Event ID: {event_id}"

    except Exception as e:
        return f"❌ Failed to schedule automation: {str(e)}"


@mcp.tool()
def list_todays_automations() -> str:
    """List all automations scheduled for today"""
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        db_path = "asgard_schedule.db"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name, drone, schedule_time, created_by 
            FROM scheduled_events 
            WHERE enabled = 1 AND (
                days LIKE '%daily%' OR 
                days LIKE ? OR
                id LIKE ?
            )
            ORDER BY schedule_time
        """,
            (f'%{datetime.now().strftime("%A").lower()}%', f"%{date}%"),
        )

        events = cursor.fetchall()
        conn.close()

        if not events:
            return "No automations scheduled for today."

        result = "📅 Today's Scheduled Automations:\n\n"
        for event in events:
            name, drone, time, creator = event
            result += f"• {time} - {name} ({drone}) [by {creator}]\n"

        return result

    except Exception as e:
        return f"❌ Failed to list automations: {str(e)}"


@mcp.tool()
def get_integration_status() -> Dict[str, Any]:
    """Get status of all integrations"""
    integrations = {
        "weather": {
            "name": "OpenWeather",
            "configured": bool(os.environ.get("OPENWEATHER_API_KEY")),
            "tools": ["get_weather", "get_weather_forecast"],
        },
        "spotify": {
            "name": "Spotify",
            "configured": bool(os.environ.get("SPOTIFY_CLIENT_ID") and os.environ.get("SPOTIFY_CLIENT_SECRET")),
            "tools": ["get_spotify_recommendations"],
        },
        "calendar": {
            "name": "Google Calendar",
            "configured": False,
            "tools": ["get_calendar_events"],
            "note": "Not yet implemented",
        },
        "core": {
            "name": "Core Tools",
            "configured": True,
            "tools": ["get_current_time", "web_search", "create_artwork", "search_local_events"],
        },
        "automation": {
            "name": "Automation",
            "configured": True,
            "tools": ["schedule_automation", "list_todays_automations"],
        },
    }

    return {"integrations": integrations, "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    # Run the MCP server on HTTP
    mcp.run(transport="http", port=8000)
