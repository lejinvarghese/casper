"""
Temporal Engine for Asgard
Simple scheduling system with daily plans and custom event scheduling
"""

import schedule
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)


@dataclass
class ScheduledEvent:
    id: str
    name: str
    drone: str
    prompt: str
    schedule_time: str
    days: List[str]
    enabled: bool = True
    created_by: str = "system"
    created_at: datetime = None
    last_run: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class DailyPlan:
    date: str
    events: List[ScheduledEvent]
    created_by: str
    created_at: datetime
    notes: str = ""


class TemporalEngine:
    """Simple scheduling system with daily plans and custom events"""

    def __init__(self, db_path: str = "asgard_schedule.db"):
        self.db_path = db_path
        self.events: Dict[str, ScheduledEvent] = {}
        self.scheduler_running = False
        self.scheduler_thread = None

        # Initialize database
        self._init_database()

        # Clean up any invalid entries
        self._cleanup_invalid_events()

        # Load existing events
        self._load_events_from_db()

        # Setup default daily plan
        self._setup_default_daily_plan()

    def _init_database(self):
        """Initialize SQLite database for schedules, memories, and logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Events table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scheduled_events (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                drone TEXT NOT NULL,
                prompt TEXT NOT NULL,
                schedule_time TEXT NOT NULL,
                days TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_by TEXT DEFAULT 'system',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP
            )
        """
        )

        # Daily plans table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_plans (
                date TEXT PRIMARY KEY,
                events_json TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT DEFAULT ''
            )
        """
        )

        # Execution logs table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                result TEXT,
                error TEXT
            )
        """
        )

        # Memories table (for future use)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                importance INTEGER DEFAULT 1
            )
        """
        )

        conn.commit()
        conn.close()

    def _load_events_from_db(self):
        """Load scheduled events from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scheduled_events WHERE enabled = 1")
        rows = cursor.fetchall()

        valid_days = [
            "daily",
            "weekday",
            "weekend",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

        for row in rows:
            try:
                days = json.loads(row[5])
                # Filter out invalid day formats (like specific dates)
                filtered_days = [day for day in days if day in valid_days]

                if not filtered_days:
                    logger.warning(f"Event {row[0]} has no valid days, skipping")
                    continue

                event = ScheduledEvent(
                    id=row[0],
                    name=row[1],
                    drone=row[2],
                    prompt=row[3],
                    schedule_time=row[4],
                    days=filtered_days,
                    enabled=bool(row[6]),
                    created_by=row[7],
                    created_at=datetime.fromisoformat(row[8]) if row[8] else datetime.now(),
                    last_run=datetime.fromisoformat(row[9]) if row[9] else None,
                )
                self.events[event.id] = event
            except Exception as e:
                logger.warning(f"Failed to load event from database: {e}")
                continue

        conn.close()

    def _setup_default_daily_plan(self):
        """Setup basic daily plan if none exists"""
        default_events = [
            ScheduledEvent(
                id="morning_energy",
                name="Morning Energy Boost",
                drone="freya",
                prompt="Good morning! Suggest an energizing breakfast and hydration plan for today. Keep it seasonal and quick to prepare.",
                schedule_time="08:00",
                days=["daily"],
            ),
            ScheduledEvent(
                id="day_strategy",
                name="Day Strategy Overview",
                drone="saga",
                prompt="Provide a strategic overview for today - optimal work blocks, weather considerations, and evening suggestions.",
                schedule_time="08:15",
                days=["weekday"],
            ),
            ScheduledEvent(
                id="midday_check",
                name="Midday Optimization",
                drone="saga",
                prompt="Mid-day check: suggest productivity optimizations, break timing, and energy management for the afternoon.",
                schedule_time="13:00",
                days=["weekday"],
            ),
            ScheduledEvent(
                id="evening_wind_down",
                name="Evening Transition",
                drone="freya",
                prompt="Evening nutrition and relaxation suggestions - what should I eat/drink to optimize tonight and tomorrow?",
                schedule_time="18:00",
                days=["daily"],
            ),
            ScheduledEvent(
                id="creative_spark",
                name="Creative Inspiration",
                drone="loki",
                prompt="Offer a creative challenge or artistic inspiration that matches the current season and time of day.",
                schedule_time="18:30",
                days=["monday", "wednesday", "friday"],
            ),
            ScheduledEvent(
                id="weekend_adventure",
                name="Weekend Mischief",
                drone="luci",
                prompt="It's the weekend! Suggest something spontaneous, fun, and slightly mischievous to do.",
                schedule_time="10:00",
                days=["weekend"],
            ),
        ]

        # Add events that don't exist
        for event in default_events:
            if event.id not in self.events:
                self.add_scheduled_event(event)

    def _save_event_to_db(self, event: ScheduledEvent):
        """Save event to database without scheduler registration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO scheduled_events 
            (id, name, drone, prompt, schedule_time, days, enabled, created_by, created_at, last_run)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event.id,
                event.name,
                event.drone,
                event.prompt,
                event.schedule_time,
                json.dumps(event.days),
                event.enabled,
                event.created_by,
                event.created_at.isoformat(),
                event.last_run.isoformat() if event.last_run else None,
            ),
        )

        conn.commit()
        conn.close()

    def add_scheduled_event(self, event: ScheduledEvent):
        """Add a new scheduled event"""
        self.events[event.id] = event

        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO scheduled_events 
            (id, name, drone, prompt, schedule_time, days, enabled, created_by, created_at, last_run)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event.id,
                event.name,
                event.drone,
                event.prompt,
                event.schedule_time,
                json.dumps(event.days),
                event.enabled,
                event.created_by,
                event.created_at.isoformat(),
                event.last_run.isoformat() if event.last_run else None,
            ),
        )

        conn.commit()
        conn.close()

        # Register with scheduler
        self._register_event_with_scheduler(event)

        logger.info(f"Added scheduled event: {event.name} at {event.schedule_time}")

    def _register_event_with_scheduler(self, event: ScheduledEvent):
        """Register event with the schedule library"""
        if not event.enabled:
            return

        for day in event.days:
            if day == "daily":
                schedule.every().day.at(event.schedule_time).do(self._execute_event, event.id)
            elif day == "weekday":
                for weekday in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                    getattr(schedule.every(), weekday).at(event.schedule_time).do(self._execute_event, event.id)
            elif day == "weekend":
                schedule.every().saturday.at(event.schedule_time).do(self._execute_event, event.id)
                schedule.every().sunday.at(event.schedule_time).do(self._execute_event, event.id)
            elif day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                # Valid day name
                getattr(schedule.every(), day).at(event.schedule_time).do(self._execute_event, event.id)
            else:
                # Skip invalid day formats (like specific dates "2025-07-02")
                logger.warning(f"Skipping invalid day format for event {event.id}: {day}")
                continue

    def _execute_event(self, event_id: str):
        """Mark event as ready for execution and return the event"""
        if event_id not in self.events:
            return None

        event = self.events[event_id]

        # Check if we've already run this today (prevent duplicates)
        if event.last_run and event.last_run.date() == datetime.now().date():
            return None

        logger.info(f"Scheduled event ready for execution: {event.name}")

        # Just return the event - the AutomationOrchestrator will handle actual execution
        return event

    def _log_execution(self, event_id: str, success: bool, result: str = None, error: str = None):
        """Log event execution to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO execution_logs (event_id, success, result, error)
            VALUES (?, ?, ?, ?)
        """,
            (event_id, success, result, error),
        )

        conn.commit()
        conn.close()

    def start_scheduler(self):
        """Start the scheduler in a background thread"""
        if self.scheduler_running:
            return

        self.scheduler_running = True

        # Clear existing schedule
        schedule.clear()

        # Register all events
        for event in self.events.values():
            self._register_event_with_scheduler(event)

        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

        logger.info("Temporal engine scheduler started")

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        schedule.clear()
        logger.info("Temporal engine scheduler stopped")

    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds

    def get_pending_events(self) -> List[ScheduledEvent]:
        """Get events ready to trigger now (called by AutomationOrchestrator)"""
        now = datetime.now()
        current_day = now.strftime("%A").lower()
        is_weekend = now.weekday() >= 5

        pending = []

        for event in self.events.values():
            if not event.enabled:
                continue

            # Check if we've already run this today
            if event.last_run and event.last_run.date() == now.date():
                continue

            # Check if time matches (within 2 minutes to avoid missing events)
            event_time = datetime.strptime(event.schedule_time, "%H:%M").time()
            current_time = now.time()

            time_diff = abs(
                (datetime.combine(now.date(), current_time) - datetime.combine(now.date(), event_time)).total_seconds()
            )

            if time_diff > 120:  # More than 2 minutes
                continue

            # Check day matches
            day_matches = False
            for day in event.days:
                if day == "daily":
                    day_matches = True
                elif day == "weekday" and not is_weekend:
                    day_matches = True
                elif day == "weekend" and is_weekend:
                    day_matches = True
                elif day == current_day:
                    day_matches = True

            if day_matches:
                pending.append(event)
                logger.info(f"Event {event.name} is pending execution")

        return pending

    def toggle_event(self, event_id: str, enabled: bool) -> bool:
        """Enable/disable specific event"""
        if event_id in self.events:
            self.events[event_id].enabled = enabled

            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE scheduled_events SET enabled = ? WHERE id = ?", (enabled, event_id))
            conn.commit()
            conn.close()

            # Restart scheduler to update registrations
            if self.scheduler_running:
                self.stop_scheduler()
                self.start_scheduler()

            logger.info(f"Event {event_id} {'enabled' if enabled else 'disabled'}")
            return True
        return False

    def get_next_event(self) -> Optional[Dict]:
        """Get the next scheduled event"""
        now = datetime.now()
        next_event = None
        next_time = None

        for event in self.events.values():
            if not event.enabled:
                continue

            # Calculate next run time for each day the event is scheduled
            for day in event.days:
                if day == "daily":
                    days_to_check = list(range(7))  # All days
                elif day == "weekday":
                    days_to_check = list(range(5))  # Monday to Friday
                elif day == "weekend":
                    days_to_check = [5, 6]  # Saturday, Sunday
                else:
                    # Specific day
                    day_map = {
                        "monday": 0,
                        "tuesday": 1,
                        "wednesday": 2,
                        "thursday": 3,
                        "friday": 4,
                        "saturday": 5,
                        "sunday": 6,
                    }
                    days_to_check = [day_map.get(day, -1)]

                for target_day in days_to_check:
                    if target_day == -1:
                        continue

                    # Calculate next occurrence
                    days_ahead = target_day - now.weekday()
                    if days_ahead < 0:  # Target day already happened this week
                        days_ahead += 7
                    elif days_ahead == 0:  # Today
                        # Check if time has passed
                        event_time = datetime.strptime(event.schedule_time, "%H:%M").time()
                        if now.time() > event_time:
                            days_ahead = 7  # Next week

                    target_date = now.date() + timedelta(days=days_ahead)
                    event_time = datetime.strptime(event.schedule_time, "%H:%M").time()
                    target_datetime = datetime.combine(target_date, event_time)

                    if next_time is None or target_datetime < next_time:
                        next_time = target_datetime
                        next_event = event

        if next_event:
            return {
                "name": next_event.name,
                "drone": next_event.drone,
                "scheduled_time": next_time.isoformat(),
                "time_until": str(next_time - now),
            }
        return None

    def create_custom_daily_plan(
        self, date: str, events: List[Dict], created_by: str = "odin", notes: str = ""
    ) -> bool:
        """Create a custom daily plan (typically by Odin)"""
        try:
            # Parse the date to get day of week
            from datetime import datetime as dt

            date_obj = dt.strptime(date, "%Y-%m-%d")
            day_name = date_obj.strftime("%A").lower()

            # Convert event dicts to ScheduledEvent objects
            scheduled_events = []
            for event_data in events:
                event = ScheduledEvent(
                    id=f"custom_{date}_{event_data['id']}",
                    name=event_data["name"],
                    drone=event_data["drone"],
                    prompt=event_data["prompt"],
                    schedule_time=event_data["schedule_time"],
                    days=[day_name],  # Day of week, not specific date
                    created_by=created_by,
                )
                scheduled_events.append(event)
                # Add to temporal engine events but don't register with scheduler yet
                self.events[event.id] = event
                self._save_event_to_db(event)

            # Save daily plan
            plan = DailyPlan(
                date=date, events=scheduled_events, created_by=created_by, created_at=datetime.now(), notes=notes
            )

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            events_json = json.dumps([asdict(event) for event in scheduled_events], default=str)

            cursor.execute(
                """
                INSERT OR REPLACE INTO daily_plans (date, events_json, created_by, notes)
                VALUES (?, ?, ?, ?)
            """,
                (date, events_json, created_by, notes),
            )

            conn.commit()
            conn.close()

            logger.info(f"Created custom daily plan for {date} by {created_by}")
            return True

        except Exception as e:
            logger.error(f"Failed to create daily plan: {e}")
            return False

    def get_daily_plan(self, date: str) -> Optional[DailyPlan]:
        """Get daily plan for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM daily_plans WHERE date = ?", (date,))
        row = cursor.fetchone()

        if row:
            events_data = json.loads(row[1])
            events = [ScheduledEvent(**event_data) for event_data in events_data]

            return DailyPlan(
                date=row[0], events=events, created_by=row[2], created_at=datetime.fromisoformat(row[3]), notes=row[4]
            )

        conn.close()
        return None

    def _cleanup_invalid_events(self):
        """Clean up events with invalid day formats that can't be scheduled"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all events
            cursor.execute("SELECT id, days FROM scheduled_events")
            rows = cursor.fetchall()

            valid_days = [
                "daily",
                "weekday",
                "weekend",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            events_to_clean = []

            for row in rows:
                event_id, days_json = row
                try:
                    days = json.loads(days_json)
                    # Check if any day is invalid (like a specific date)
                    has_invalid_days = any(day not in valid_days for day in days)
                    if has_invalid_days:
                        # Filter to only valid days
                        valid_filtered_days = [day for day in days if day in valid_days]
                        if valid_filtered_days:
                            # Update with only valid days
                            cursor.execute(
                                "UPDATE scheduled_events SET days = ? WHERE id = ?",
                                (json.dumps(valid_filtered_days), event_id),
                            )
                            logger.info(f"Cleaned invalid days from event {event_id}")
                        else:
                            # No valid days, disable the event
                            cursor.execute("UPDATE scheduled_events SET enabled = 0 WHERE id = ?", (event_id,))
                            logger.warning(f"Disabled event {event_id} - no valid days found")

                except (json.JSONDecodeError, TypeError):
                    # Invalid JSON, disable the event
                    cursor.execute("UPDATE scheduled_events SET enabled = 0 WHERE id = ?", (event_id,))
                    logger.warning(f"Disabled event {event_id} - invalid days JSON")

            conn.commit()
            conn.close()
            logger.info("Completed cleanup of invalid events")

        except Exception as e:
            logger.error(f"Failed to cleanup invalid events: {e}")

    def get_automation_status(self) -> Dict:
        """Get current automation system status"""
        now = datetime.now()
        pending = self.get_pending_events()
        next_event = self.get_next_event()

        return {
            "context": {
                "current_time": now.isoformat(),
                "time_segment": self._get_time_segment(now),
                "day_of_week": now.weekday(),
                "is_weekend": now.weekday() >= 5,
                "date": now.strftime("%Y-%m-%d"),
            },
            "pending_count": len(pending),
            "pending_automations": [
                {"id": event.id, "name": event.name, "drone": event.drone, "type": "scheduled"} for event in pending
            ],
            "next_automation": next_event,
            "total_automations": len(self.events),
            "enabled_automations": len([e for e in self.events.values() if e.enabled]),
            "scheduler_running": self.scheduler_running,
        }

    def _get_time_segment(self, dt: datetime) -> str:
        """Get current time segment"""
        hour = dt.hour
        if 5 <= hour < 9:
            return "morning"
        elif 9 <= hour < 17:
            return "workday"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
