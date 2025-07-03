"""
Asgard Tools - Specialized tools for drone operations
"""

import os
import asyncio
import sqlite3
import json
from datetime import datetime
from smolagents import tool, Tool
from tavily import TavilyClient

from src.utils.secrets import get_secret
from src.tools.image import generate_image


class TavilySearchTool(Tool):
    name = "web_search"
    description = "Performs a web search using Tavily AI and returns formatted search results."
    inputs = {"query": {"type": "string", "description": "The search query to perform."}}
    output_type = "string"

    def __init__(self, max_results: int = 5):
        super().__init__()
        self.max_results = max_results

    def forward(self, query: str) -> str:
        """Forward method required by Tool base class"""
        try:
            api_key = os.environ.get("TAVILY_API_KEY")
            if not api_key:
                return "❌ Tavily API key not found. Add TAVILY_API_KEY to your .env file."

            tavily_client = TavilyClient(api_key=api_key)
            response = tavily_client.search(query, max_results=self.max_results)

            return self.parse_results(response)

        except Exception as e:
            return f"❌ Search failed: {str(e)}"

    def parse_results(self, response) -> str:
        """Parse Tavily response into markdown format"""
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


@tool
def create_artwork(prompt: str, style: str = "realistic", enhance: bool = True) -> str:
    """Create artwork using AI image generation

    Args:
        prompt: Description of the artwork to create
        style: Art style (realistic, fantasy, abstract, etc.)
        enhance: Whether to enhance the prompt for better results
    """
    try:
        # Load .env from asgard folder specifically
        from dotenv import load_dotenv

        asgard_env_path = os.path.join(os.path.dirname(__file__), ".env")
        load_dotenv(asgard_env_path)

        # Get API key
        api_key = os.environ.get("RUNWARE_API_KEY")
        if not api_key:
            return "❌ Artwork creation failed: Missing API Key. Get one at https://my.runware.ai/signup"

        enhanced_prompt = f"{prompt}, {style} style, high quality, detailed"

        # Create a new event loop for this thread to avoid conflict
        import threading

        def run_image_generation():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(generate_image(prompt=enhanced_prompt, enhance=enhance, n_results=1))
            finally:
                new_loop.close()

        # Run in a separate thread to avoid event loop conflicts
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_image_generation)
            images = future.result(timeout=60)  # 60 second timeout

        return f"🎨 Artwork created: {images[0].imageURL}" if images else "❌ Failed to create artwork"
    except Exception as e:
        return f"❌ Artwork creation failed: {str(e)}"


@tool
def get_current_time() -> str:
    """Get current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def search_local_events(location: str, activity_type: str = "any") -> str:
    """Search for local events and activities

    Args:
        location: Location to search for events
        activity_type: Type of activity (food, entertainment, sports, etc.)
    """
    search_tool = TavilySearchTool()
    return search_tool(f"local events {activity_type} {location} this weekend")


@tool
def schedule_automation(name: str, drone: str, prompt: str, schedule_time: str, notes: str = "") -> str:
    """Schedule a new automation event for today

    Args:
        name: Name of the automation event
        drone: Which drone to use (freya, saga, loki, mimir, luci)
        prompt: The prompt/task for the drone to execute
        schedule_time: Time to run in HH:MM format (e.g., "15:30")
        notes: Optional notes about this automation
    """
    try:
        # Get current date
        date = datetime.now().strftime("%Y-%m-%d")

        # Database path (same as temporal engine)
        db_path = "asgard_schedule.db"

        # Create unique ID
        event_id = f"odin_{date}_{name.lower().replace(' ', '_')}"

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get day of week
        day_name = datetime.now().strftime("%A").lower()

        # Insert into scheduled_events
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

        # Insert into daily_plans
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


@tool
def list_todays_automations() -> str:
    """List all automations scheduled for today"""
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        db_path = "asgard_schedule.db"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get today's scheduled events
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


def get_search_tool():
    """Returns the configured search tool for all agents"""
    return TavilySearchTool()


def get_automation_tools():
    """Returns automation scheduling tools for Odin"""
    return [schedule_automation, list_todays_automations]
