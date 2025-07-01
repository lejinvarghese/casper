"""
Asgard Citadel Tools - Specialized tools for drone operations
"""

import os
import asyncio
from datetime import datetime
from smolagents import tool, Tool
from tavily import TavilyClient

from src.utils.secrets import get_secret
from src.tools.image import generate_image


# Tavily search tool following smolagents Tool interface
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
        enhanced_prompt = f"{prompt}, {style} style, high quality, detailed"
        images = asyncio.run(generate_image(prompt=enhanced_prompt, enhance=enhance, n_results=1))
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


def get_search_tool():
    """Returns the configured search tool for all agents"""
    return TavilySearchTool()
