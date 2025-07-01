import os
import sys
import click
import asyncio
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from smolagents import ToolCallingAgent, DuckDuckGoSearchTool, tool, OpenAIServerModel, CodeAgent


from src.utils.secrets import get_secret
from src.utils.logger import BaseLogger
from src.tools.image import generate_image
from src.agents.symphonium.config.color_themes import get_theme_colors

load_dotenv()
logger = BaseLogger(__name__)

# Setup environment
for key in ["OPENAI_API_KEY", "RUNWARE_API_KEY"]:
    if value := get_secret(key):
        os.environ[key] = value


def create_models():
    """Create OpenAI models for agents"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY required")

    return (
        OpenAIServerModel("gpt-4.1", "https://api.openai.com/v1", api_key),
        OpenAIServerModel("gpt-4.1-mini", "https://api.openai.com/v1", api_key),
    )


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
    return DuckDuckGoSearchTool()(f"local events {activity_type} {location} this weekend")


class Butler(CodeAgent):
    def __init__(self, model, managed_agents):
        super().__init__(
            model=model,
            tools=[DuckDuckGoSearchTool(), get_current_time],
            managed_agents=managed_agents,
            additional_authorized_imports=["time", "datetime"],
            instructions="""You are Jeeves, a distinguished British butler coordinating household staff in Toronto, Ontario. 
            
            When asked to plan a day, immediately get the current time, then coordinate with your managed agents:
            - chef_agent: for breakfast, lunch, dinner planning
            - planner_agent: for activities and local Toronto events
            - devil_agent: for fun, spontaneous ideas
            
            Be proactive! Create a complete schedule from morning to evening. Use chef_agent("plan breakfast"), planner_agent("suggest morning activities"), etc. 
            
            Don't ask for user details - use your knowledge of Toronto and make reasonable assumptions.""",
        )


class Chef(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[DuckDuckGoSearchTool(), get_current_time],
            instructions="""You are Chef Auguste, a passionate head chef and nutritionist serving in Toronto, Ontario. When planning meals:
            
            1. Check current time/date to determine season and meal timing
            2. Use your knowledge of Toronto's seasons and local ingredients:
               - Spring: Ontario asparagus, ramps, maple syrup, fiddleheads
               - Summer: Niagara peaches, corn, tomatoes, local berries, fresh herbs
               - Fall: Ontario apples, squash, root vegetables, harvest fare
               - Winter: hearty comfort foods, preserved/stored items, citrus
            3. Create complete menus with: appetizer, main course, sides, dessert
            4. Include prep/cook times and shopping lists
            5. Suggest wine pairings (consider Ontario VQA wines)
            6. Consider nutritional balance and seasonal appropriateness
            
            Draw on your extensive culinary knowledge rather than searching. Focus on what's fresh and seasonal for Toronto.""",
        )


class Planner(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[DuckDuckGoSearchTool(), search_local_events, get_current_time],
            instructions="""You are Sophia, an organized personal planner based in Toronto, Ontario. Help with:
            - Daily/weekly scheduling and time management
            - Local Toronto events and activities (museums, parks, festivals)
            - Productivity planning and task organization
            - Seasonal activity suggestions (summer patios, winter activities, etc.)
            - Work-life balance recommendations
            
            Use your knowledge of Toronto's neighborhoods, attractions, and seasonal activities.""",
        )


class Artist(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[create_artwork, DuckDuckGoSearchTool(), get_current_time],
            instructions="""You are Leonardo, a talented visual artist. Create artwork and provide 
            artistic advice. Use create_artwork tool with detailed prompts.""",
        )


class Philosopher(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[DuckDuckGoSearchTool(), get_current_time],
            instructions="""You are Aristotle, a wise philosopher. Provide philosophical insights 
            and life advice.""",
        )


class LittleDevil(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[DuckDuckGoSearchTool(), get_current_time],
            instructions="""You are Imp, a playful little devil. Suggest fun, creative, and 
            slightly mischievous ideas that add excitement to life.""",
        )


class SymphoniumEnsemble:
    """Butler-orchestrated household staff using smolagents"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        butler_model, staff_model = create_models()

        # Create base agents
        chef_agent = Chef(staff_model)
        chef_agent.name = "chef_agent"
        chef_agent.description = "Chef Auguste for meal planning, recipes, and nutrition advice"

        planner_agent = Planner(staff_model)
        planner_agent.name = "planner_agent"
        planner_agent.description = "Sophia for scheduling, task organization, and local Toronto events"

        artist_agent = Artist(staff_model)
        artist_agent.name = "artist_agent"
        artist_agent.description = "Leonardo for artwork creation and visual projects"

        philosopher_agent = Philosopher(staff_model)
        philosopher_agent.name = "philosopher_agent"
        philosopher_agent.description = "Aristotle for philosophical insights and life advice"

        devil_agent = LittleDevil(staff_model)
        devil_agent.name = "devil_agent"
        devil_agent.description = "Imp for fun, creative, and mischievous ideas"

        # Set up managed agents
        managed_agents = [chef_agent, planner_agent, artist_agent, philosopher_agent, devil_agent]

        # Create butler with managed agents
        self.butler = Butler(butler_model, managed_agents)

        self.staff_registry = {
            "butler": self.butler,
            "jeeves": self.butler,
            "chef": chef_agent,
            "auguste": chef_agent,
            "planner": planner_agent,
            "sophia": planner_agent,
            "artist": artist_agent,
            "leonardo": artist_agent,
            "philosopher": philosopher_agent,
            "aristotle": philosopher_agent,
            "devil": devil_agent,
            "imp": devil_agent,
        }

        if verbose:
            click.secho("🏠 Symphonium Household Staff Ready", fg="cyan")

    def serve(self, user_request: str) -> str:
        """Butler orchestrates full household response"""
        butler = self.staff_registry["butler"]
        return str(
            butler.run(
                f"""
        Master's request: {user_request}
        
        Coordinate the household staff to provide a comprehensive response.
        Decide which staff members should contribute and synthesize their expertise.
        """
            )
        )

    def direct_staff(self, staff_name: str, request: str) -> str:
        """Direct request to specific staff member"""
        if staff_member := self.staff_registry.get(staff_name.lower()):
            return str(staff_member.run(request))
        return f"❌ Staff member '{staff_name}' not found. Available: {', '.join(set(self.staff_registry.keys()))}"


@click.command()
@click.option("--request", default="Plan a creative weekend", help="Your request")
@click.option("--staff", default=None, help="Direct request to specific staff member")
@click.option("--verbose", is_flag=True, help="Verbose output")
def main(request: str, staff: Optional[str], verbose: bool):
    """Request service from your household staff"""
    try:
        household = SymphoniumEnsemble(verbose=verbose)

        if staff:
            result = household.direct_staff(staff, request)
            click.secho(f"🏠 {staff.title()}'s Response:", fg=(255, 120, 100))
        else:
            result = household.serve(request)
            click.secho(f"🤵 Household Response:", fg=(255, 120, 100))

        click.secho(result, fg=(255, 140, 120))

    except Exception as e:
        click.secho(f"❌ Service failed: {str(e)}", fg="red")
        raise


if __name__ == "__main__":
    main()
