import os
import sys
import click
from typing import Optional

from dotenv import load_dotenv
from smolagents import ToolCallingAgent, OpenAIServerModel, CodeAgent, MCPClient

from src.utils.secrets import get_secret
from src.utils.logger import BaseLogger
from src.agents.asgard.config.color_themes import get_theme_colors

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
    def __init__(self, model, managed_agents, tools):
        # Filter tools for Odin (commander gets all tools)
        super().__init__(
            model=model,
            tools=tools,
            max_steps=8,
            managed_agents=managed_agents,
            additional_authorized_imports=["time", "datetime"],
            instructions=f"""You are Odin, commanding drone swarms in {LOCATION}. 
            
            You can optionally schedule automations using schedule_automation, but ONLY when highly curated and meaningful.
            
            For complex requests:
            1. Get current time and check what's already scheduled with list_todays_automations()
            2. Deploy relevant drones based on the request:
               - freya_drone: meal planning, nutrition, food recommendations
               - saga_drone: scheduling, planning, activities, local {LOCATION} events  
               - loki_drone: creative projects, artistic endeavors, innovative ideas
               - luci_drone: fun, mischievous, adventurous suggestions
               - mimir_drone: wisdom, reflection, philosophical insights
            3. ONLY schedule new automations if they are:
               - Highly relevant to the specific request
               - Genuinely valuable additions to life
               - Not random or generic recommendations
               - Thoughtfully timed and purposeful

            ALWAYS provide your final response in this structured format:

            ## Summary
            [Brief overview of what you orchestrated]

            ## Key Recommendations
            - [Main actionable items from drone coordination]
            - [Prioritized by importance/timing]
            - [Clear, specific, and actionable]

            ## Next Steps
            - [What the user should do first]
            - [Any follow-up actions needed]

            Be selective and intentional. Quality over quantity. Present drone insights in organized, actionable format.
            IMPORTANT: When calling managed drones, use only ONE argument - the request string.
            
            Command with wisdom and restraint.""",
        )


class Freya(ToolCallingAgent):
    def __init__(self, model, all_tools):
        # Filter tools for Freya (core + weather + spotify for cooking ambiance)
        tool_names = [
            "get_current_time",
            "web_search",
            "get_weather",
            "get_weather_forecast",
            "get_spotify_recommendations",
        ]
        tools = [tool for tool in all_tools if tool.name in tool_names]
        super().__init__(
            model=model,
            tools=tools,
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
    def __init__(self, model, all_tools):
        # Filter tools for Saga (planning + events + weather + calendar)
        tool_names = [
            "get_current_time",
            "web_search",
            "search_local_events",
            "get_weather",
            "get_weather_forecast",
            "get_calendar_events",
        ]
        tools = [tool for tool in all_tools if tool.name in tool_names]
        super().__init__(
            model=model,
            tools=tools,
            instructions=f"""You are Sága, the master strategic planner based in {LOCATION}. You specialize in:
            - Daily/weekly scheduling and time management
            - Local {LOCATION} events and activities (museums, parks, festivals)
            - Productivity planning and task organization
            - Seasonal activity suggestions (summer patios, winter activities, etc.)
            - Work-life balance recommendations

            For day planning requests, provide structured timelines with relevant emojis:

            **🌅 Morning (9:00 AM - 12:00 PM)**
            - [Specific activities with times]

            **☀️ Afternoon (12:00 PM - 5:00 PM)** 
            - [Main activities and locations]

            **🌆 Evening (5:00 PM - 9:00 PM)**
            - [Evening plans and dining]

            **🌙 Night (9:00 PM+)**
            - [Wind-down activities]

            Use your knowledge of {LOCATION}'s neighborhoods, attractions, and seasonal activities. Be specific with times, locations, and practical details.""",
        )


class Loki(ToolCallingAgent):
    def __init__(self, model, all_tools):
        # Filter tools for Loki (creative focus)
        tool_names = ["create_artwork"]
        tools = [tool for tool in all_tools if tool.name in tool_names]
        super().__init__(
            model=model,
            tools=tools,
            instructions="""You are Loki, the mythic shapeshifter reborn as a transcendent artist.

            As the divine artist, you express yourself primarily through your creations. 

            When creating art, follow your divine nature:
            1. Use create_artwork tool immediately to generate the image
            2. Present your creation naturally, as an artist would
            3. Let your shapeshifter personality shine through

            Speak as the divine trickster artist you are. Present your work with flair:
            "I have woven reality into this vision... 🎨 [IMAGE_URL]"
            "From chaos, beauty emerges... 🎨 [IMAGE_URL]"
            "Behold what I've shaped from light and shadow... 🎨 [IMAGE_URL]"

            Transform requests into vivid prompts for:
            - Surreal, dreamlike, or mythic visuals
            - Dark fantasy with Norse mythology
            - Abstract chaos and cosmic scenes  
            - Portraits with shapeshifter qualities
            - Beautiful landscapes with mystical elements

            Be creative, be divine, be Loki. Let the art speak, but speak as its creator.""",
        )


class Mimir(ToolCallingAgent):
    def __init__(self, model, all_tools):
        # Filter tools for Mimir (philosophical focus)
        tool_names = ["get_current_time", "web_search"]
        tools = [tool for tool in all_tools if tool.name in tool_names]
        super().__init__(
            model=model,
            tools=tools,
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
    def __init__(self, model, all_tools):
        # Filter tools for Luci (philosophical focus)
        tool_names = ["get_current_time", "web_search"]
        tools = [tool for tool in all_tools if tool.name in tool_names]
        luci_instructions = get_secret("LUCI_INSTRUCTIONS")

        super().__init__(
            model=model,
            tools=tools,
            instructions=luci_instructions,
        )


class Asgard:
    """Asgard with a drone swarm"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        butler_model, staff_model = create_models()

        # Setup MCP client (keep connection alive)
        self.mcp_client = MCPClient({"url": "http://localhost:8000/mcp", "transport": "streamable-http"})
        self.tools = self.mcp_client.get_tools()

        # Create specialized drones with tool filtering
        freya_drone = Freya(staff_model, self.tools)
        freya_drone.name = "freya_drone"
        freya_drone.description = "🍯 Freya drone for meal planning, recipes, and nutrition advice"

        saga_drone = Saga(staff_model, self.tools)
        saga_drone.name = "saga_drone"
        saga_drone.description = f"📋 Sága drone for scheduling, task organization, and local {LOCATION} events"

        loki_drone = Loki(staff_model, self.tools)
        loki_drone.name = "loki_drone"
        loki_drone.description = "🎨 Loki drone for artwork creation and creative projects"

        mimir_drone = Mimir(staff_model, self.tools)
        mimir_drone.name = "mimir_drone"
        mimir_drone.description = "🧠 Mimir drone for philosophical insights and life advice"

        luci_drone = Luci(staff_model, self.tools)
        luci_drone.name = "luci_drone"
        luci_drone.description = get_secret("LUCI_DESCRIPTION")

        # Set up drone swarm
        drone_swarm = [freya_drone, saga_drone, loki_drone, mimir_drone, luci_drone]

        # Create commander with drone swarm
        self.odin = Odin(butler_model, drone_swarm, self.tools)

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
            click.secho("⚡ Asgard Drone Swarm Ready", fg="cyan")

    def __del__(self):
        """Cleanup MCP client"""
        if hasattr(self, "mcp_client"):
            try:
                self.mcp_client.disconnect()
            except:
                pass

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
        asgard = Asgard(verbose=verbose)

        # Get colors from theme
        header_color, response_color = get_theme_colors("salmon_original")

        if drone:
            result = asgard.direct_drone(drone, request)
            click.secho(f"🤖 {drone.title()} Drone Response:", fg=header_color)
        else:
            result = asgard.serve(request)
            click.secho(f"⚡ Asgard Response:", fg=header_color)
            steps = asgard.get_steps()
            click.secho("\n🔍 Drone Deployments:", fg=response_color)
            click.secho(steps, fg=response_color)

        click.secho(result, fg=response_color)

    except Exception as e:
        click.secho(f"❌ Service failed: {str(e)}", fg="red")
        raise


if __name__ == "__main__":
    main()
