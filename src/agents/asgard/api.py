"""
FastAPI server for Asgard
Provides REST API interface to the drone swarm coordination system
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
from src.agents.asgard.citadel import Asgard
from src.agents.asgard.automation import AutomationOrchestrator


load_dotenv()
# load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))  # Load from asgard folder


class RequestModel(BaseModel):
    request: str
    drone: Optional[str] = None
    verbose: bool = False


class ConfigModel(BaseModel):
    theme: Optional[str] = "salmon_original"
    location: Optional[str] = "Toronto, Ontario"
    verbose: bool = False


class AsgardService:
    """Service class to manage Asgard instance"""

    def __init__(self):
        self._asgard: Optional[Asgard] = None
        self._automation_orchestrator: Optional[AutomationOrchestrator] = None

    def initialize(self, verbose: bool = False) -> None:
        """Initialize Asgard and automation system"""
        self._asgard = Asgard(verbose=verbose)
        self._automation_orchestrator = AutomationOrchestrator(self._asgard)
        self._automation_orchestrator.start_background_automations()

    def get_asgard(self) -> Asgard:
        """Get the Asgard instance"""
        if self._asgard is None:
            raise HTTPException(status_code=500, detail="Asgard not initialized")
        return self._asgard

    def get_automation_orchestrator(self) -> AutomationOrchestrator:
        """Get the automation orchestrator instance"""
        if self._automation_orchestrator is None:
            raise HTTPException(status_code=500, detail="Automation system not initialized")
        return self._automation_orchestrator

    def reconfigure(self, verbose: bool = False) -> None:
        """Reconfigure Asgard"""
        if self._automation_orchestrator:
            self._automation_orchestrator.stop_background_automations()
        self._asgard = Asgard(verbose=verbose)
        self._automation_orchestrator = AutomationOrchestrator(self._asgard)
        # Don't auto-start background automations on reconfigure


# Service instance
asgard_service = AsgardService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asgard_service.initialize(verbose=False)
    yield
    # Shutdown (cleanup if needed)
    pass


def get_asgard_service() -> AsgardService:
    """Dependency to get Asgard service"""
    return asgard_service


app = FastAPI(title="Asgard API", description="Drone Swarm Coordination API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Asgard API", "status": "active"}


@app.get("/drones")
async def get_drones():
    """Get list of available drones"""
    return {
        "drones": {
            "odin": "⚡ Commander - orchestrates swarm coordination",
            "freya": "🍯 Culinary Expert - meal planning, nutrition, and delicious recipes",
            "saga": "📋 Strategic Planner - scheduling, coordination, and local events",
            "loki": "🎨 Creative Innovator - artwork, visual projects, and bold ideas",
            "mimir": "🧠 Wise Counselor - philosophy, insights, and thoughtful guidance",
            "luci": "😈 Mischief Maker - adventure, creativity, and delightful chaos",
        },
        "aliases": {
            "commander": "odin",
            "chef": "freya",
            "planner": "saga",
            "artist": "loki",
            "philosopher": "mimir",
            "devil": "luci",
        },
    }


@app.post("/request")
async def handle_request(request_data: RequestModel, service: AsgardService = Depends(get_asgard_service)):
    """Handle user request through drone swarm"""
    try:
        print(f"API received: drone='{request_data.drone}', request='{request_data.request}'")  # Debug log
        asgard = service.get_asgard()

        if request_data.drone:
            # Direct drone request
            print(f"Directing to drone: {request_data.drone}")  # Debug log
            result = asgard.direct_drone(request_data.drone, request_data.request)
            steps = None
        else:
            # Full swarm deployment
            print("Using full swarm deployment (Odin)")  # Debug log
            result = asgard.serve(request_data.request)
            steps = asgard.get_steps()
            print(f"🔍 Backend API - Steps generated: {repr(steps)}")  # Debug log
            print(f"🔍 Backend API - Steps length: {len(steps) if steps else 'None'}")  # Debug log

        response_data = {
            "success": True,
            "result": result,
            "steps": steps,
            "drone_used": request_data.drone or "odin (full swarm deployment)",
        }
        print(f"🔍 Backend API - Full response: {response_data}")  # Debug log
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/configure")
async def configure_asgard(config: ConfigModel, service: AsgardService = Depends(get_asgard_service)):
    """Configure Asgard settings"""
    try:
        service.reconfigure(verbose=config.verbose)
        return {"success": True, "config": config.dict(), "message": "Asgard reconfigured"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check(service: AsgardService = Depends(get_asgard_service)):
    """Health check endpoint"""
    try:
        # Try to get Asgard - will raise exception if not initialized
        service.get_asgard()
        return {"status": "healthy", "asgard_ready": True}
    except HTTPException:
        return {"status": "healthy", "asgard_ready": False}


@app.get("/automations/status")
async def get_automation_status(service: AsgardService = Depends(get_asgard_service)):
    """Get automation system status"""
    try:
        orchestrator = service.get_automation_orchestrator()
        status = orchestrator.get_automation_status()
        return {"success": True, **status}
    except Exception as e:
        import traceback

        print(f"Error in get_automation_status: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/automations/recent")
async def get_recent_automations(hours: int = 24, service: AsgardService = Depends(get_asgard_service)):
    """Get recent automation executions"""
    try:
        orchestrator = service.get_automation_orchestrator()
        recent = orchestrator.get_recent_automations(hours)
        return {"success": True, "automations": recent}
    except Exception as e:
        import traceback

        print(f"Error in get_recent_automations: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automations/{automation_id}/toggle")
async def toggle_automation(automation_id: str, enabled: bool, service: AsgardService = Depends(get_asgard_service)):
    """Enable or disable a specific automation"""
    try:
        orchestrator = service.get_automation_orchestrator()
        result = orchestrator.toggle_automation(automation_id, enabled)
        if result:
            return {"success": True, "automation_id": automation_id, "enabled": enabled}
        else:
            raise HTTPException(status_code=404, detail="Automation not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automations/{automation_id}/trigger")
async def trigger_automation(automation_id: str, service: AsgardService = Depends(get_asgard_service)):
    """Manually trigger an automation"""
    try:
        orchestrator = service.get_automation_orchestrator()
        result = orchestrator.trigger_automation_now(automation_id)
        if result:
            return {"success": True, "result": result}
        else:
            raise HTTPException(status_code=404, detail="Automation not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/automations/{automation_id}")
async def get_automation_details(automation_id: str, service: AsgardService = Depends(get_asgard_service)):
    """Get details for a specific automation"""
    try:
        orchestrator = service.get_automation_orchestrator()
        details = orchestrator.get_automation_details(automation_id)
        if details:
            return {"success": True, "automation": details}
        else:
            raise HTTPException(status_code=404, detail="Automation not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automations/background/start")
async def start_background_automations(service: AsgardService = Depends(get_asgard_service)):
    """Manually start background automation loop"""
    try:
        orchestrator = service.get_automation_orchestrator()
        orchestrator.start_background_automations()
        return {"success": True, "message": "Background automations started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automations/background/stop")
async def stop_background_automations(service: AsgardService = Depends(get_asgard_service)):
    """Manually stop background automation loop"""
    try:
        orchestrator = service.get_automation_orchestrator()
        orchestrator.stop_background_automations()
        return {"success": True, "message": "Background automations stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automations/test")
async def test_automation_system(service: AsgardService = Depends(get_asgard_service)):
    """Test the automation system by triggering a simple automation"""
    try:
        orchestrator = service.get_automation_orchestrator()

        # Create a test event
        from src.agents.asgard.automation import ScheduledEvent

        test_event = ScheduledEvent(
            id="test_automation",
            name="Test Automation",
            drone="freya",
            prompt="This is a test automation. Please respond with 'Test automation executed successfully!'",
            schedule_time="00:00",  # Won't be used for manual trigger
            days=["daily"],
        )

        # Execute it manually
        orchestrator._execute_event(test_event)

        # Get recent results
        recent = orchestrator.get_recent_automations(1)

        return {
            "success": True,
            "message": "Test automation executed",
            "recent_count": len(recent),
            "recent_results": recent[:3],  # Show first 3 results
        }
    except Exception as e:
        import traceback

        print(f"Error in test automation: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/automations")
async def debug_automation_data(service: AsgardService = Depends(get_asgard_service)):
    """Debug endpoint to see what's in the database"""
    try:
        orchestrator = service.get_automation_orchestrator()

        # Get raw database data
        import sqlite3

        conn = sqlite3.connect(orchestrator.temporal_engine.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM execution_logs ORDER BY executed_at DESC LIMIT 5")
        execution_logs = cursor.fetchall()

        cursor.execute("SELECT * FROM scheduled_events LIMIT 5")
        scheduled_events = cursor.fetchall()

        cursor.execute("SELECT * FROM daily_plans ORDER BY created_at DESC LIMIT 3")
        daily_plans = cursor.fetchall()

        conn.close()

        # Get processed recent automations
        recent = orchestrator.get_recent_automations(24)

        # Get memory results
        memory_results = list(orchestrator.automation_results.values())

        # Get temporal engine status
        temporal_status = orchestrator.temporal_engine.get_automation_status()

        return {
            "success": True,
            "database": {
                "path": orchestrator.temporal_engine.db_path,
                "execution_logs": execution_logs,
                "scheduled_events": scheduled_events,
                "daily_plans": daily_plans,
            },
            "processed_data": {
                "recent_automations": recent,
                "memory_results": memory_results,
                "temporal_status": temporal_status,
            },
            "system_info": {
                "scheduler_running": orchestrator.temporal_engine.scheduler_running,
                "background_running": orchestrator.is_running,
                "total_events": len(orchestrator.temporal_engine.events),
            },
        }
    except Exception as e:
        import traceback

        print(f"Error in debug endpoint: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automations/custom-plan")
async def create_custom_plan(plan_data: dict, service: AsgardService = Depends(get_asgard_service)):
    """Create a custom daily plan (typically via Odin)"""
    try:
        orchestrator = service.get_automation_orchestrator()

        # Extract plan details
        date = plan_data.get("date")
        events = plan_data.get("events", [])
        notes = plan_data.get("notes", "")
        created_by = plan_data.get("created_by", "odin")

        if not date or not events:
            raise HTTPException(status_code=400, detail="Date and events are required")

        # Create the custom plan
        success = orchestrator.create_custom_plan(date, events, notes)

        if success:
            return {
                "success": True,
                "message": f"Custom plan created for {date}",
                "events_count": len(events),
                "created_by": created_by,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create custom plan")

    except Exception as e:
        import traceback

        print(f"Error creating custom plan: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automations/reload")
async def reload_automations(service: AsgardService = Depends(get_asgard_service)):
    """Reload automations from database to pick up new events"""
    try:
        orchestrator = service.get_automation_orchestrator()
        success = orchestrator.reload_events_from_database()

        if success:
            return {"success": True, "message": "Automations reloaded from database"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reload automations")

    except Exception as e:
        import traceback

        print(f"Error reloading automations: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug/steps")
async def debug_steps(request_data: RequestModel, service: AsgardService = Depends(get_asgard_service)):
    """Debug endpoint to check step format"""
    try:
        asgard = service.get_asgard()

        # Make a test request
        result = asgard.serve("Plan a simple dinner")
        steps = asgard.get_steps()

        # Get raw memory steps for comparison
        raw_steps = asgard.odin.memory.get_full_steps()

        return {
            "success": True,
            "result": result,
            "formatted_steps": steps,
            "raw_steps": [str(step) for step in raw_steps],
            "raw_steps_count": len(raw_steps),
            "formatted_steps_lines": steps.split("\n") if steps else [],
        }
    except Exception as e:
        import traceback

        print(f"Error in debug steps: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.agents.asgard.api:app", host="0.0.0.0", port=port, reload=True)
