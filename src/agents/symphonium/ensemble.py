import os
import sys
import click
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv
from smolagents import ToolCallingAgent, MultiStepAgent, DuckDuckGoSearchTool, tool, OpenAIServerModel

# # Add project root to path if running as main
# if __name__ == "__main__":
#     sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from src.utils.secrets import get_secret
from src.utils.logger import BaseLogger
from src.tools.image import generate_image

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
        OpenAIServerModel("gpt-4o", "https://api.openai.com/v1", api_key),
        OpenAIServerModel("gpt-4o-mini", "https://api.openai.com/v1", api_key)
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

class Butler(MultiStepAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[DuckDuckGoSearchTool(), get_current_time],
            instructions="""You are Jeeves, a distinguished British butler. Coordinate household staff efficiently:
            - Chef Auguste: food, nutrition, meal planning  
            - Sophia: planning, scheduling, local events
            - Leonardo: artwork, visual creativity
            - Aristotle: philosophical insights, life advice
            - Imp: playful ideas, creative mischief"""
        )
    
    def initialize_system_prompt(self):
        return self.instructions

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
            
            Draw on your extensive culinary knowledge rather than searching. Focus on what's fresh and seasonal for Toronto."""
        )

class Planner(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[DuckDuckGoSearchTool(), search_local_events, get_current_time],
            instructions="""You are Sophia, an organized personal planner. Help with task organization, 
            scheduling, and finding local events."""
        )

class Artist(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[create_artwork, DuckDuckGoSearchTool(), get_current_time],
            instructions="""You are Leonardo, a talented visual artist. Create artwork and provide 
            artistic advice. Use create_artwork tool with detailed prompts."""
        )

class Philosopher(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[DuckDuckGoSearchTool(), get_current_time],
            instructions="""You are Aristotle, a wise philosopher. Provide philosophical insights 
            and life advice."""
        )

class LittleDevil(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[DuckDuckGoSearchTool(), get_current_time],
            instructions="""You are Imp, a playful little devil. Suggest fun, creative, and 
            slightly mischievous ideas that add excitement to life."""
        )

class SymphoniumEnsemble:
    """Butler-orchestrated household staff using smolagents"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        butler_model, staff_model = create_models()
        
        self.staff_registry = {
            "butler": Butler(butler_model),
            "jeeves": Butler(butler_model),
            "chef": Chef(staff_model),
            "auguste": Chef(staff_model),
            "planner": Planner(staff_model),
            "sophia": Planner(staff_model),
            "artist": Artist(staff_model),
            "leonardo": Artist(staff_model),
            "philosopher": Philosopher(staff_model),
            "aristotle": Philosopher(staff_model),
            "devil": LittleDevil(staff_model),
            "imp": LittleDevil(staff_model)
        }
        
        if verbose:
            click.secho("🏠 Symphonium Household Staff Ready", fg="cyan")
    
    def serve(self, user_request: str) -> str:
        """Butler orchestrates full household response"""
        butler = self.staff_registry["butler"]
        return str(butler.run(f"""
        Master's request: {user_request}
        
        Coordinate the household staff to provide a comprehensive response.
        Decide which staff members should contribute and synthesize their expertise.
        """))
    
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
            click.secho(f"🏠 {staff.title()}'s Response:", fg="blue")
        else:
            result = household.serve(request)
            click.secho(f"🤵 Household Response:", fg="blue")
        
        click.secho(result, fg="white")
        
    except Exception as e:
        click.secho(f"❌ Service failed: {str(e)}", fg="red")
        raise

if __name__ == "__main__":
    main()