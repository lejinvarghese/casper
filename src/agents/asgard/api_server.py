"""
FastAPI server for Symphonium Ensemble
Provides REST API interface to the Norse mythology agent ensemble
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import asyncio
from ensemble import AsgardNexus

app = FastAPI(title="Symphonium API", description="Norse Mythology Agent Ensemble API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ensemble
ensemble = None


class RequestModel(BaseModel):
    request: str
    staff: Optional[str] = None
    verbose: bool = False


class ConfigModel(BaseModel):
    theme: Optional[str] = "salmon_original"
    location: Optional[str] = "Toronto, Ontario"
    verbose: bool = False


@app.on_event("startup")
async def startup_event():
    global ensemble
    ensemble = AsgardNexus(verbose=False)


@app.get("/")
async def root():
    return {"message": "Symphonium Ensemble API", "status": "active"}


@app.get("/agents")
async def get_agents():
    """Get list of available agents"""
    return {
        "agents": {
            "odin": "Coordinating leader - manages all other agents",
            "freya": "Chef and nutritionist - meal planning and recipes",
            "saga": "Personal planner - scheduling and local events",
            "loki": "Creative artist - artwork and visual projects",
            "mimir": "Philosopher - wisdom and life advice",
            "luci": "Mischievous demon - fun and adventurous ideas",
        },
        "aliases": {
            "coordinator": "odin",
            "chef": "freya",
            "planner": "saga",
            "artist": "loki",
            "philosopher": "mimir",
            "devil": "luci",
        },
    }


@app.post("/request")
async def handle_request(request_data: RequestModel):
    """Handle user request through ensemble"""
    try:
        if not ensemble:
            raise HTTPException(status_code=500, detail="Ensemble not initialized")

        if request_data.staff:
            # Direct staff request
            result = ensemble.direct_staff(request_data.staff, request_data.request)
            steps = None
        else:
            # Full ensemble coordination
            result = ensemble.serve(request_data.request)
            steps = ensemble.get_steps()

        return {
            "success": True,
            "result": result,
            "steps": steps,
            "staff_used": request_data.staff or "odin (coordinator)",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/configure")
async def configure_ensemble(config: ConfigModel):
    """Configure ensemble settings"""
    try:
        global ensemble
        ensemble = SymphoniumEnsemble(verbose=config.verbose)
        return {"success": True, "config": config.dict(), "message": "Ensemble reconfigured"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "ensemble_ready": ensemble is not None}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
