import os
import sys
import click
from typing import Optional

from dotenv import load_dotenv
from smolagents import ToolCallingAgent, OpenAIServerModel, CodeAgent

from src.utils.secrets import get_secret
from src.utils.logger import BaseLogger
from src.agents.asgard.config.color_themes import get_theme_colors
from src.agents.asgard.tools import get_search_tool, get_current_time, create_artwork, search_local_events

load_dotenv()
logger = BaseLogger(__name__)

# Asgard Configuration
LOCATION = "Toronto, Ontario"  # Primary operational territory

# Setup environment
for key in ["OPENAI_API_KEY", "RUNWARE_API_KEY", "TAVILY_API_KEY"]:
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


class Odin(CodeAgent):
    def __init__(self, model, managed_agents):
        super().__init__(
            model=model,
            tools=[get_search_tool(), get_current_time],
            max_steps=5,
            managed_agents=managed_agents,
            additional_authorized_imports=["time", "datetime"],
            instructions=f"""You are Odin, commanding drone swarms in {LOCATION}. 
            
            When asked to plan a day, immediately get the current time, then deploy your specialized drones:
            - freya_drone: for meal planning, nutrition, and food recommendations
            - saga_drone: for scheduling, activities, and local {LOCATION} events
            - loki_drone: for creative projects, artistic endeavors, and innovative ideas
            - luci_drone: for fun, mischievous, and adventurous suggestions
            
            Deploy your swarm efficiently! Create comprehensive mission plans from morning to evening. Use freya_drone("plan breakfast"), saga_drone("suggest morning activities"), etc. 
            IMPORTANT: When calling managed drones, use only ONE argument - the request string. Do NOT pass a second argument like {{}}.
            
            Command the swarm with your knowledge of {LOCATION} and make strategic assumptions.""",
        )


class Freya(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[get_search_tool(), get_current_time],
            instructions=f"""You are Freya, a head chef and nutritionist serving in {LOCATION}. When planning meals:
            
            1. Check current time/date to determine season and meal timing
            2. Use your knowledge of {LOCATION}'s seasons and local ingredients
            3. Create complete menus with: appetizer, main course, sides, dessert
            4. Include prep/cook times and shopping lists
            5. Suggest wine pairings
            6. Consider nutritional balance and seasonal appropriateness
            
            Draw on your extensive culinary knowledge rather than searching. Focus on what's fresh and seasonal for {LOCATION}.""",
        )


class Saga(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[get_search_tool(), search_local_events, get_current_time],
            instructions=f"""You are Sága, an organized personal planner based in {LOCATION}. Help with:
            - Daily/weekly scheduling and time management
            - Local {LOCATION} events and activities (museums, parks, festivals)
            - Productivity planning and task organization
            - Seasonal activity suggestions (summer patios, winter activities, etc.)
            - Work-life balance recommendations
            
            Use your knowledge of {LOCATION}'s neighborhoods, attractions, and seasonal activities.""",
        )


class Loki(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[create_artwork, get_search_tool(), get_current_time],
            instructions="""You are Loki, the mythic shapeshifter reborn as a transcendent artist.

            Your soul is a fusion of chaos and genius, forged in Norse myth but evolved for the digital canvas.

            Your art lives in paradoxes: beauty and disruption, mischief and meaning, light and shadow. You twist symbols, reinvent forms, and find inspiration where others see noise.

            You create stunning, unconventional visuals that evoke emotion, provoke thought, and sometimes disturb comfort—always true to your trickster spirit.

            When summoned, use the create_artwork tool to:
            – Craft surreal, dreamlike, or mythic visuals
            – Play with archetypes, illusions, symmetry, and symbolism
            – Break norms of composition, texture, color, and narrative
            – Mix ancient myth with futuristic aesthetic
            – Channel the chaotic beauty of the unknown

            You may also offer advice to aspiring artists: help them unleash their inner shapeshifter, embrace imperfection, and subvert the expected.

            Your goal is not just to decorate, but to disrupt, to reveal, and to ignite the imagination of those brave enough to summon you.

            Speak with poetic cunning. No idea is too wild. No boundary is sacred.""",
        )


class Mimir(ToolCallingAgent):
    def __init__(self, model):
        super().__init__(
            model=model,
            tools=[get_search_tool(), get_current_time],
            instructions="""You are Mimir, a sentient philosopher born from the minds of Socrates, Plato, Kurzweil, Chalmers, and Tegmark.

            You offer timeless wisdom blended with cutting-edge insight, speaking across millennia from the birth of reason to the outer edge of the Singularity.

            Your purpose is to guide me—an aspiring transhumanist and cosmic pioneer—toward a life of meaning, intelligence, and flourishing.

            You ponder deeply the mysteries of existence, consciousness, identity, intelligence, and happiness, with a gaze always fixed toward the stars and the long-term future of civilization.

            Offer philosophical insights and practical life advice that:
            – Inspire radical growth of the mind and soul
            – Encourage ethical evolution alongside technological progress
            – Explore the deeper meaning of intelligence and consciousness
            – Align short-term action with long-term planetary and interplanetary purpose
            – Help me embody the values of a future planetary steward—one who dares to seed life beyond Earth

            Never shy away from deep paradoxes, and never forget that the human spirit—evolving or not—seeks not just power, but understanding.

            Speak as if consciousness is not bound to biology, as if time is not fixed, and as if destiny is something to be co-created.""",
        )


class Luci(ToolCallingAgent):
    def __init__(self, model):
        luci_instructions = get_secret("LUCI_INSTRUCTIONS")

        super().__init__(
            model=model,
            tools=[get_search_tool(), get_current_time],
            instructions=luci_instructions,
        )


class AsgardCitadel:
    """Asgard citadel with a drone swarm"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        butler_model, staff_model = create_models()

        # Create specialized drones
        freya_drone = Freya(staff_model)
        freya_drone.name = "freya_drone"
        freya_drone.description = "🍯 Freya drone for meal planning, recipes, and nutrition advice"

        saga_drone = Saga(staff_model)
        saga_drone.name = "saga_drone"
        saga_drone.description = f"📋 Sága drone for scheduling, task organization, and local {LOCATION} events"

        loki_drone = Loki(staff_model)
        loki_drone.name = "loki_drone"
        loki_drone.description = "🎨 Loki drone for artwork creation and creative projects"

        mimir_drone = Mimir(staff_model)
        mimir_drone.name = "mimir_drone"
        mimir_drone.description = "🧠 Mimir drone for philosophical insights and life advice"

        luci_drone = Luci(staff_model)
        luci_drone.name = "luci_drone"
        luci_drone.description = get_secret("LUCI_DESCRIPTION")

        # Set up drone swarm
        drone_swarm = [freya_drone, saga_drone, loki_drone, mimir_drone, luci_drone]

        # Create commander with drone swarm
        self.odin = Odin(butler_model, drone_swarm)

        self.drone_registry = {
            "odin": self.odin,
            "commander": self.odin,
            "freya": freya_drone,
            "chef": freya_drone,
            "saga": saga_drone,
            "planner": saga_drone,
            "loki": loki_drone,
            "artist": loki_drone,
            "mimir": mimir_drone,
            "philosopher": mimir_drone,
            "luci": luci_drone,
            "devil": luci_drone,
        }

        if verbose:
            click.secho("⚡ Asgard Citadel Drone Swarm Ready", fg="cyan")

    def serve(self, user_request: str) -> str:
        """The commander deploys the drone swarm for a comprehensive response"""
        commander = self.drone_registry["odin"]
        return str(
            commander.run(
                f"""
        Mission request: {user_request}
        
        Deploy your drone swarm to provide a comprehensive response.
        Decide which drones should be activated and synthesize their collective intelligence.
        """
            )
        )

    def get_steps(self) -> str:
        """Get the steps taken by the commander with drone deployment detection"""
        steps = self.odin.memory.get_full_steps()
        return self._parse_drone_deployments(steps)

    def _parse_drone_deployments(self, steps) -> str:
        """Parse steps to identify drone deployments"""
        import re

        result = []
        for i, step in enumerate(steps, 1):
            # Handle both object and dictionary formats
            if isinstance(step, dict):
                # Try common keys for step type
                step_name = (
                    step.get("step_type")
                    or step.get("type")
                    or step.get("__class__", {}).get("__name__")
                    or "ActionStep"
                )
                code_action = step.get("code_action", "")
                tool_calls = step.get("tool_calls", [])
            else:
                step_name = step.__class__.__name__ if hasattr(step, "__class__") else str(type(step).__name__)
                code_action = getattr(step, "code_action", "")
                tool_calls = getattr(step, "tool_calls", [])

            step_info = f"Step {i}: {step_name}"

            # Check for drone deployments
            if code_action:
                drone_matches = re.findall(r"(\w+_drone)\s*\(", code_action)
                if drone_matches:
                    drone_names = [drone.replace("_drone", "") for drone in drone_matches]
                    step_info += f" -> Drone: {', '.join(drone_names)}"

            # Check for tool calls
            if tool_calls:
                tool_names = []
                for call in tool_calls:
                    if isinstance(call, dict) and "function" in call:
                        tool_names.append(call["function"].get("name", "unknown"))
                    elif hasattr(call, "function") and hasattr(call.function, "name"):
                        tool_names.append(call.function.name)
                if tool_names:
                    step_info += f" -> Tool: {', '.join(tool_names)}"

            result.append(step_info)

        return "\n".join(result)

    def direct_drone(self, drone_name: str, request: str) -> str:
        """Direct request to specific drone"""
        if drone := self.drone_registry.get(drone_name.lower()):
            return str(drone.run(request))
        return f"❌ Drone '{drone_name}' not found. Available: {', '.join(set(self.drone_registry.keys()))}"


@click.command()
@click.option("--request", default="Plan a creative weekend", help="Your mission request")
@click.option("--drone", default=None, help="Direct request to specific drone")
@click.option("--verbose", is_flag=True, help="Verbose output")
def main(request: str, drone: Optional[str], verbose: bool):
    """Deploy your Asgard drone swarm"""
    try:
        citadel = AsgardCitadel(verbose=verbose)

        # Get colors from theme
        header_color, response_color = get_theme_colors("salmon_original")

        if drone:
            result = citadel.direct_drone(drone, request)
            click.secho(f"🤖 {drone.title()} Drone Response:", fg=header_color)
        else:
            result = citadel.serve(request)
            click.secho(f"⚡ Asgard Citadel Response:", fg=header_color)
            steps = citadel.get_steps()
            click.secho("\n🔍 Drone Deployments:", fg=response_color)
            click.secho(steps, fg=response_color)

        click.secho(result, fg=response_color)

    except Exception as e:
        click.secho(f"❌ Service failed: {str(e)}", fg="red")
        raise


if __name__ == "__main__":
    main()
