"""
Automation Orchestrator for Asgard Citadel
Manages background automation execution and scheduling
"""

import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from src.agents.asgard.temporal_engine import TemporalEngine, ProactiveAutomation, AutomationContext
from src.agents.asgard.citadel import AsgardCitadel
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)


class AutomationOrchestrator:
    """Orchestrates background automation execution"""

    def __init__(self, citadel: AsgardCitadel):
        self.citadel = citadel
        self.temporal_engine = TemporalEngine()
        self.is_running = False
        self.automation_thread = None
        self.automation_results: Dict[str, Dict] = {}
        self.notification_callbacks: List[Callable] = []

    def start_background_automations(self):
        """Start the background automation loop"""
        if self.is_running:
            logger.warning("Automations already running")
            return

        self.is_running = True
        self.automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
        self.automation_thread.start()
        logger.info("Background automations started")

    def stop_background_automations(self):
        """Stop the background automation loop"""
        self.is_running = False
        if self.automation_thread:
            self.automation_thread.join(timeout=5)
        logger.info("Background automations stopped")

    def _automation_loop(self):
        """Main automation execution loop"""
        while self.is_running:
            try:
                context = self.temporal_engine.get_current_context()
                pending_automations = self.temporal_engine.get_pending_automations(context)

                for automation in pending_automations:
                    if not self.is_running:
                        break

                    self._execute_automation(automation, context)

                # Sleep for 30 minutes before checking again
                for _ in range(1800):  # 30 minutes in seconds
                    if not self.is_running:
                        break
                    threading.Event().wait(1)

            except Exception as e:
                logger.error(f"Error in automation loop: {e}")
                threading.Event().wait(60)  # Wait 1 minute on error

    def _execute_automation(self, automation: ProactiveAutomation, context: AutomationContext):
        """Execute a single automation"""
        try:
            logger.info(f"Executing automation: {automation.name} via {automation.drone}")

            # Execute the automation prompt through the citadel
            if automation.drone == "odin":
                # Full swarm coordination
                result = self.citadel.serve(automation.prompt)
                steps = self.citadel.get_steps()
            else:
                # Direct drone request
                result = self.citadel.direct_drone(automation.drone, automation.prompt)
                steps = None

            # Store the result
            automation_result = {
                "automation_id": automation.id,
                "automation_name": automation.name,
                "drone": automation.drone,
                "executed_at": context.current_time.isoformat(),
                "time_segment": context.time_segment.value,
                "result": result,
                "steps": steps,
                "success": True,
            }

            self.automation_results[automation.id] = automation_result

            # Mark as triggered
            self.temporal_engine.mark_triggered(automation.id, context.current_time)

            # Notify any registered callbacks
            self._notify_callbacks(automation_result)

            logger.info(f"Successfully executed automation: {automation.name}")

        except Exception as e:
            logger.error(f"Failed to execute automation {automation.name}: {e}")

            # Store error result
            error_result = {
                "automation_id": automation.id,
                "automation_name": automation.name,
                "drone": automation.drone,
                "executed_at": context.current_time.isoformat(),
                "time_segment": context.time_segment.value,
                "error": str(e),
                "success": False,
            }

            self.automation_results[automation.id] = error_result

    def _notify_callbacks(self, result: Dict):
        """Notify registered callbacks of automation results"""
        for callback in self.notification_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Error in automation callback: {e}")

    def register_notification_callback(self, callback: Callable):
        """Register a callback for automation notifications"""
        self.notification_callbacks.append(callback)

    def get_recent_automations(self, hours: int = 24) -> List[Dict]:
        """Get automations executed in the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)

        recent = []
        for result in self.automation_results.values():
            executed_at = datetime.fromisoformat(result["executed_at"].replace("Z", "+00:00"))
            if executed_at >= cutoff:
                recent.append(result)

        # Sort by execution time, most recent first
        recent.sort(key=lambda x: x["executed_at"], reverse=True)
        return recent

    def get_automation_status(self) -> Dict:
        """Get comprehensive automation system status"""
        temporal_status = self.temporal_engine.get_automation_status()
        recent_automations = self.get_recent_automations(24)

        return {
            **temporal_status,
            "background_running": self.is_running,
            "recent_automations": recent_automations[:5],  # Last 5 automations
            "total_executed_today": len(
                [
                    a
                    for a in recent_automations
                    if datetime.fromisoformat(a["executed_at"].replace("Z", "+00:00")).date() == datetime.now().date()
                ]
            ),
        }

    def toggle_automation(self, automation_id: str, enabled: bool) -> bool:
        """Enable/disable specific automation"""
        return self.temporal_engine.toggle_automation(automation_id, enabled)

    def trigger_automation_now(self, automation_id: str) -> Optional[Dict]:
        """Manually trigger an automation immediately"""
        if automation_id not in self.temporal_engine.automations:
            return None

        automation = self.temporal_engine.automations[automation_id]
        context = self.temporal_engine.get_current_context()

        # Temporarily enable and execute
        original_enabled = automation.enabled
        automation.enabled = True

        try:
            self._execute_automation(automation, context)
            return self.automation_results.get(automation_id)
        finally:
            automation.enabled = original_enabled

    def get_automation_details(self, automation_id: str) -> Optional[Dict]:
        """Get details for a specific automation"""
        if automation_id not in self.temporal_engine.automations:
            return None

        automation = self.temporal_engine.automations[automation_id]
        recent_result = self.automation_results.get(automation_id)

        return {
            "id": automation.id,
            "name": automation.name,
            "drone": automation.drone,
            "prompt": automation.prompt,
            "time_segments": [seg.value for seg in automation.time_segments],
            "automation_type": automation.automation_type.value,
            "enabled": automation.enabled,
            "last_triggered": automation.last_triggered.isoformat() if automation.last_triggered else None,
            "cooldown_hours": automation.cooldown_hours,
            "last_result": recent_result,
        }
