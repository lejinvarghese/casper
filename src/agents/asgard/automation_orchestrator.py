"""
Automation Orchestrator for Asgard
Manages background automation execution and scheduling
"""

import threading
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from src.agents.asgard.temporal_engine import TemporalEngine, ScheduledEvent
from src.agents.asgard.citadel import Asgard
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)


class AutomationOrchestrator:
    """Orchestrates background automation execution"""

    def __init__(self, asgard: Asgard):
        self.asgard = asgard
        self.temporal_engine = TemporalEngine()
        self.is_running = False
        self.automation_thread = None
        self.automation_results: Dict[str, Dict] = {}
        self.notification_callbacks: List[Callable] = []

    def start_background_automations(self):
        """Start the background automation system"""
        if self.is_running:
            logger.warning("Automations already running")
            return

        self.is_running = True
        # Start the temporal engine scheduler
        self.temporal_engine.start_scheduler()

        # Start our monitoring loop
        self.automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
        self.automation_thread.start()
        logger.info("Background automations started")

    def stop_background_automations(self):
        """Stop the background automation system"""
        self.is_running = False

        # Stop the temporal engine scheduler
        self.temporal_engine.stop_scheduler()

        if self.automation_thread:
            self.automation_thread.join(timeout=5)
        logger.info("Background automations stopped")

    def _automation_loop(self):
        """Monitor for pending events and execute them"""
        while self.is_running:
            try:
                # Check for pending events
                pending_events = self.temporal_engine.get_pending_events()

                for event in pending_events:
                    if not self.is_running:
                        break

                    self._execute_event(event)

                # Sleep for 1 minute before checking again
                for _ in range(60):  # 1 minute in seconds
                    if not self.is_running:
                        break
                    threading.Event().wait(1)

            except Exception as e:
                logger.error(f"Error in automation loop: {e}")
                threading.Event().wait(60)  # Wait 1 minute on error

    def _execute_event(self, event: ScheduledEvent):
        """Execute a single scheduled event"""
        try:
            logger.info(f"Executing event: {event.name} via {event.drone}")

            # Execute the event prompt through Asgard
            if event.drone == "odin":
                # Full swarm coordination
                result = self.asgard.serve(event.prompt)
                steps = self.asgard.get_steps()
            else:
                # Direct drone request
                result = self.asgard.direct_drone(event.drone, event.prompt)
                steps = None

            # Store the result
            execution_result = {
                "automation_id": event.id,
                "automation_name": event.name,
                "drone": event.drone,
                "executed_at": datetime.now().isoformat(),
                "result": result,
                "steps": steps,
                "success": True,
            }

            self.automation_results[event.id] = execution_result

            # Update event's last run time and save to database
            event.last_run = datetime.now()
            self._save_execution_to_db(event.id, execution_result)

            # Notify any registered callbacks
            self._notify_callbacks(execution_result)

            logger.info(f"Successfully executed event: {event.name}")

        except Exception as e:
            logger.error(f"Failed to execute event {event.name}: {e}")

            # Store error result
            error_result = {
                "automation_id": event.id,
                "automation_name": event.name,
                "drone": event.drone,
                "executed_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
            }

            self.automation_results[event.id] = error_result
            self._save_execution_to_db(event.id, error_result)

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

    def _save_execution_to_db(self, event_id: str, result: Dict):
        """Save execution result to database"""
        try:
            conn = sqlite3.connect(self.temporal_engine.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO execution_logs (event_id, success, result, error)
                VALUES (?, ?, ?, ?)
            """,
                (
                    event_id,
                    result.get("success", False),
                    (
                        json.dumps(result)
                        if result.get("success")
                        else json.dumps({"error": result.get("error", "Unknown error")})
                    ),
                    result.get("error", None),
                ),
            )

            conn.commit()
            conn.close()
            logger.debug(f"Saved execution result for {event_id} to database")
        except Exception as e:
            logger.error(f"Failed to save execution result to database: {e}")

    def _load_recent_from_db(self, hours: int = 24) -> List[Dict]:
        """Load recent automation executions from database"""
        try:
            conn = sqlite3.connect(self.temporal_engine.db_path)
            cursor = conn.cursor()

            # Get recent executions from the last N hours
            cutoff = datetime.now() - timedelta(hours=hours)

            cursor.execute(
                """
                SELECT el.id, el.event_id, el.executed_at, el.success, el.result, el.error, se.name, se.drone 
                FROM execution_logs el
                LEFT JOIN scheduled_events se ON el.event_id = se.id
                WHERE el.executed_at >= ?
                ORDER BY el.executed_at DESC
            """,
                (cutoff.isoformat(),),
            )

            rows = cursor.fetchall()

            recent = []
            for row in rows:
                try:
                    # Parse result data if it exists and is a string
                    result_data = {}
                    if row[4] and isinstance(row[4], str):  # el.result is column 4
                        try:
                            result_data = json.loads(row[4])
                        except json.JSONDecodeError as e:
                            logger.warning(f"Could not parse result JSON: {e}")
                            result_data = {"result": str(row[4])}  # Fallback to string

                    automation_result = {
                        "automation_id": row[1],  # el.event_id
                        "automation_name": row[6] or "Unknown",  # se.name
                        "drone": row[7] or "unknown",  # se.drone
                        "executed_at": row[2] or datetime.now().isoformat(),  # el.executed_at
                        "success": bool(row[3]),  # el.success
                        "result": result_data.get("result", ""),
                        "steps": result_data.get("steps"),
                        "error": row[5] if row[5] else None,  # el.error
                    }
                    recent.append(automation_result)
                except Exception as e:
                    logger.warning(f"Could not parse execution result from database row: {e}, row: {row}")
                    continue

            conn.close()
            return recent

        except Exception as e:
            logger.error(f"Failed to load recent automations from database: {e}")
            return []

    def get_recent_automations(self, hours: int = 24) -> List[Dict]:
        """Get automations executed in the last N hours from database and memory"""
        # First try to load from database
        db_recent = self._load_recent_from_db(hours)

        # If database has results, use those
        if db_recent:
            logger.debug(f"Loaded {len(db_recent)} recent automations from database")
            return db_recent

        # Fallback to memory (for backwards compatibility)
        logger.debug("No database results found, checking memory...")
        cutoff = datetime.now() - timedelta(hours=hours)

        recent = []
        for result in self.automation_results.values():
            # Parse the ISO format datetime string
            executed_at_str = result.get("executed_at")
            if not executed_at_str:
                continue

            if executed_at_str.endswith("Z"):
                executed_at_str = executed_at_str[:-1] + "+00:00"

            try:
                executed_at = datetime.fromisoformat(executed_at_str)
                # Make both datetimes timezone-naive for comparison
                if executed_at.tzinfo is not None:
                    executed_at = executed_at.replace(tzinfo=None)

                if executed_at >= cutoff:
                    recent.append(result)
            except (ValueError, AttributeError) as e:
                logger.warning(f"Could not parse executed_at time: {executed_at_str}, error: {e}")
                continue

        # Sort by execution time, most recent first
        recent.sort(key=lambda x: x["executed_at"], reverse=True)
        logger.debug(f"Loaded {len(recent)} recent automations from memory")
        return recent

    def get_automation_status(self) -> Dict:
        """Get comprehensive automation system status"""
        temporal_status = self.temporal_engine.get_automation_status()
        recent_automations = self.get_recent_automations(24)

        # Count today's executions
        today_count = 0
        today = datetime.now().date()

        for automation in recent_automations:
            try:
                executed_at_str = automation.get("executed_at")
                if not executed_at_str:
                    continue

                if executed_at_str.endswith("Z"):
                    executed_at_str = executed_at_str[:-1] + "+00:00"

                executed_at = datetime.fromisoformat(executed_at_str)
                if executed_at.tzinfo is not None:
                    executed_at = executed_at.replace(tzinfo=None)

                if executed_at.date() == today:
                    today_count += 1
            except (ValueError, KeyError, AttributeError):
                continue

        return {
            **temporal_status,
            "background_running": self.is_running,
            "recent_automations": recent_automations[:5],  # Last 5 automations
            "total_executed_today": today_count,
        }

    def toggle_automation(self, automation_id: str, enabled: bool) -> bool:
        """Enable/disable specific automation"""
        return self.temporal_engine.toggle_event(automation_id, enabled)

    def trigger_automation_now(self, automation_id: str) -> Optional[Dict]:
        """Manually trigger an automation immediately"""
        if automation_id not in self.temporal_engine.events:
            return None

        event = self.temporal_engine.events[automation_id]

        # Temporarily enable and execute
        original_enabled = event.enabled
        event.enabled = True

        try:
            self._execute_event(event)
            return self.automation_results.get(automation_id)
        finally:
            event.enabled = original_enabled

    def get_automation_details(self, automation_id: str) -> Optional[Dict]:
        """Get details for a specific automation"""
        if automation_id not in self.temporal_engine.events:
            return None

        event = self.temporal_engine.events[automation_id]
        recent_result = self.automation_results.get(automation_id)

        return {
            "id": event.id,
            "name": event.name,
            "drone": event.drone,
            "prompt": event.prompt,
            "schedule_time": event.schedule_time,
            "days": event.days,
            "enabled": event.enabled,
            "created_by": event.created_by,
            "last_triggered": event.last_run.isoformat() if event.last_run else None,
            "last_result": recent_result,
        }

    def create_custom_plan(self, date: str, events: List[Dict], notes: str = "") -> bool:
        """Create a custom daily plan (for Odin)"""
        return self.temporal_engine.create_custom_daily_plan(date, events, "odin", notes)

    def get_daily_plan(self, date: str) -> Optional[Dict]:
        """Get daily plan for a specific date"""
        plan = self.temporal_engine.get_daily_plan(date)
        if plan:
            return {
                "date": plan.date,
                "events": [
                    {
                        "id": event.id,
                        "name": event.name,
                        "drone": event.drone,
                        "schedule_time": event.schedule_time,
                        "prompt": event.prompt,
                    }
                    for event in plan.events
                ],
                "created_by": plan.created_by,
                "created_at": plan.created_at.isoformat(),
                "notes": plan.notes,
            }
        return None

    def reload_events_from_database(self):
        """Reload events from database to pick up new automations created by Odin"""
        try:
            # Reload events in temporal engine
            self.temporal_engine._load_events_from_db()

            # Restart scheduler to register new events
            if self.temporal_engine.scheduler_running:
                self.temporal_engine.stop_scheduler()
                self.temporal_engine.start_scheduler()

            logger.info("Reloaded automation events from database")
            return True
        except Exception as e:
            logger.error(f"Failed to reload events from database: {e}")
            return False
