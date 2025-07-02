#!/usr/bin/env python3
"""
Simple script to start the Asgard Citadel backend server
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

if __name__ == "__main__":
    import uvicorn
    from src.agents.asgard.api import app

    print("🏰 Starting Asgard Citadel API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔗 Health check: http://localhost:8000/health")
    print("🤖 Automation status: http://localhost:8000/automations/status")
    print("\nPress Ctrl+C to stop the server")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
