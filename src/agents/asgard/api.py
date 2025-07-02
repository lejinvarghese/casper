"""
FastAPI server for Asgard Citadel
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
from src.agents.asgard.citadel import AsgardCitadel
from src.agents.asgard.automation_orchestrator import AutomationOrchestrator


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


class CitadelService:
    """Service class to manage Asgard Citadel instance"""

    def __init__(self):
        self._citadel: Optional[AsgardCitadel] = None
        self._automation_orchestrator: Optional[AutomationOrchestrator] = None

    def initialize(self, verbose: bool = False) -> None:
        """Initialize the citadel and automation system"""
        self._citadel = AsgardCitadel(verbose=verbose)
        self._automation_orchestrator = AutomationOrchestrator(self._citadel)
        self._automation_orchestrator.start_background_automations()

    def get_citadel(self) -> AsgardCitadel:
        """Get the citadel instance"""
        if self._citadel is None:
            raise HTTPException(status_code=500, detail="Citadel not initialized")
        return self._citadel

    def get_automation_orchestrator(self) -> AutomationOrchestrator:
        """Get the automation orchestrator instance"""
        if self._automation_orchestrator is None:
            raise HTTPException(status_code=500, detail="Automation system not initialized")
        return self._automation_orchestrator

    def reconfigure(self, verbose: bool = False) -> None:
        """Reconfigure the citadel"""
        if self._automation_orchestrator:
            self._automation_orchestrator.stop_background_automations()
        self._citadel = AsgardCitadel(verbose=verbose)
        self._automation_orchestrator = AutomationOrchestrator(self._citadel)
        self._automation_orchestrator.start_background_automations()


# Service instance
citadel_service = CitadelService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    citadel_service.initialize(verbose=False)
    yield
    # Shutdown (cleanup if needed)
    pass


def get_citadel_service() -> CitadelService:
    """Dependency to get citadel service"""
    return citadel_service


app = FastAPI(title="Asgard Citadel API", description="Drone Swarm Coordination API", lifespan=lifespan)

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
    return {"message": "Asgard Citadel API", "status": "active"}


@app.get("/drones")
async def get_drones():
    """Get list of available drones"""
    return {
        "drones": {
            "odin": "⚡ All-Father Commander - orchestrates drone swarm deployments",
            "freya": "🍯 Kitchen Drone - meal planning, nutrition, and recipes",
            "saga": "📋 Strategic Drone - scheduling, planning, and local events",
            "loki": "🎨 Creative Drone - artwork, visual projects, and innovation",
            "mimir": "🧠 Wisdom Drone - philosophy, insights, and life advice",
            "luci": "😈 Shadow Drone - mischief, adventure, and creative chaos",
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
async def handle_request(request_data: RequestModel, service: CitadelService = Depends(get_citadel_service)):
    """Handle user request through drone swarm"""
    try:
        print(f"API received: drone='{request_data.drone}', request='{request_data.request}'")  # Debug log
        citadel = service.get_citadel()

        if request_data.drone:
            # Direct drone request
            print(f"Directing to drone: {request_data.drone}")  # Debug log
            result = citadel.direct_drone(request_data.drone, request_data.request)
            steps = None
        else:
            # Full swarm deployment
            print("Using full swarm deployment (Odin)")  # Debug log
            result = citadel.serve(request_data.request)
            steps = citadel.get_steps()

        return {
            "success": True,
            "result": result,
            "steps": steps,
            "drone_used": request_data.drone or "odin (full swarm deployment)",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/configure")
async def configure_citadel(config: ConfigModel, service: CitadelService = Depends(get_citadel_service)):
    """Configure citadel settings"""
    try:
        service.reconfigure(verbose=config.verbose)
        return {"success": True, "config": config.dict(), "message": "Citadel reconfigured"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check(service: CitadelService = Depends(get_citadel_service)):
    """Health check endpoint"""
    try:
        # Try to get citadel - will raise exception if not initialized
        service.get_citadel()
        return {"status": "healthy", "citadel_ready": True}
    except HTTPException:
        return {"status": "healthy", "citadel_ready": False}


@app.get("/automations/status")
async def get_automation_status(service: CitadelService = Depends(get_citadel_service)):
    """Get automation system status"""
    try:
        orchestrator = service.get_automation_orchestrator()
        status = orchestrator.get_automation_status()
        return {"success": True, **status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/automations/recent")
async def get_recent_automations(hours: int = 24, service: CitadelService = Depends(get_citadel_service)):
    """Get recent automation executions"""
    try:
        orchestrator = service.get_automation_orchestrator()
        recent = orchestrator.get_recent_automations(hours)
        return {"success": True, "automations": recent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/automations/{automation_id}/toggle")
async def toggle_automation(automation_id: str, enabled: bool, service: CitadelService = Depends(get_citadel_service)):
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
async def trigger_automation(automation_id: str, service: CitadelService = Depends(get_citadel_service)):
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
async def get_automation_details(automation_id: str, service: CitadelService = Depends(get_citadel_service)):
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


if __name__ == "__main__":
    uvicorn.run("src.agents.asgard.api:app", host="0.0.0.0", port=8000, reload=True)
