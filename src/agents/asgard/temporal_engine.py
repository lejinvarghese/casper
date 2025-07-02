"""
Temporal Context Engine for Asgard Citadel
Provides time-aware, context-sensitive automation coordination
"""

import asyncio
import json
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pytz
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)


class TimeSegment(Enum):
    EARLY_MORNING = "early_morning"  # 5-7 AM
    MORNING = "morning"  # 7-9 AM
    WORKDAY = "workday"  # 9 AM - 5 PM
    EVENING = "evening"  # 5-9 PM
    NIGHT = "night"  # 9 PM - 5 AM


class AutomationType(Enum):
    PROACTIVE = "proactive"  # Automatic suggestions
    REACTIVE = "reactive"  # Response to context changes
    SCHEDULED = "scheduled"  # Fixed time triggers


@dataclass
class AutomationContext:
    current_time: datetime
    time_segment: TimeSegment
    timezone: str
    day_of_week: int
    is_weekend: bool
    season: str

    def to_dict(self) -> Dict:
        return {**asdict(self), "current_time": self.current_time.isoformat(), "time_segment": self.time_segment.value}


@dataclass
class ProactiveAutomation:
    id: str
    name: str
    drone: str
    prompt: str
    time_segments: List[TimeSegment]
    automation_type: AutomationType
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    cooldown_hours: int = 24

    def can_trigger(self, context: AutomationContext) -> bool:
        if not self.enabled:
            return False

        if context.time_segment not in self.time_segments:
            return False

        if self.last_triggered:
            time_since = context.current_time - self.last_triggered
            if time_since.total_seconds() < (self.cooldown_hours * 3600):
                return False

        return True


class TemporalEngine:
    """Manages time-aware context and automation scheduling"""

    def __init__(self, timezone: str = "America/Toronto"):
        self.timezone = pytz.timezone(timezone)
        self.automations: Dict[str, ProactiveAutomation] = {}
        self.setup_default_automations()

    def get_current_context(self) -> AutomationContext:
        """Get current temporal context"""
        now = datetime.now(self.timezone)

        return AutomationContext(
            current_time=now,
            time_segment=self._get_time_segment(now.time()),
            timezone=str(self.timezone),
            day_of_week=now.weekday(),
            is_weekend=now.weekday() >= 5,
            season=self._get_season(now.month),
        )

    def _get_time_segment(self, current_time: time) -> TimeSegment:
        """Determine current time segment"""
        hour = current_time.hour

        if 5 <= hour < 7:
            return TimeSegment.EARLY_MORNING
        elif 7 <= hour < 9:
            return TimeSegment.MORNING
        elif 9 <= hour < 17:
            return TimeSegment.WORKDAY
        elif 17 <= hour < 21:
            return TimeSegment.EVENING
        else:
            return TimeSegment.NIGHT

    def _get_season(self, month: int) -> str:
        """Get current season"""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"

    def setup_default_automations(self):
        """Setup default proactive automations"""

        self.automations = {
            "morning_energy": ProactiveAutomation(
                id="morning_energy",
                name="Morning Energy Boost",
                drone="freya",
                prompt="Good morning! Suggest an energizing breakfast and hydration plan for Toronto weather today. Keep it seasonal and quick to prepare.",
                time_segments=[TimeSegment.MORNING],
                automation_type=AutomationType.PROACTIVE,
                cooldown_hours=20,
            ),
            "day_overview": ProactiveAutomation(
                id="day_overview",
                name="Day Strategy",
                drone="saga",
                prompt="Provide a strategic overview for today in Toronto - optimal work blocks, weather considerations, and evening suggestions.",
                time_segments=[TimeSegment.MORNING],
                automation_type=AutomationType.PROACTIVE,
                cooldown_hours=20,
            ),
            "midday_optimization": ProactiveAutomation(
                id="midday_optimization",
                name="Workday Optimization",
                drone="saga",
                prompt="Mid-day check: suggest productivity optimizations, break timing, and energy management for the afternoon.",
                time_segments=[TimeSegment.WORKDAY],
                automation_type=AutomationType.PROACTIVE,
                cooldown_hours=6,
            ),
            "evening_wind_down": ProactiveAutomation(
                id="evening_wind_down",
                name="Evening Transition",
                drone="freya",
                prompt="Evening nutrition and relaxation suggestions - what should I eat/drink to optimize tonight and tomorrow?",
                time_segments=[TimeSegment.EVENING],
                automation_type=AutomationType.PROACTIVE,
                cooldown_hours=20,
            ),
            "creative_spark": ProactiveAutomation(
                id="creative_spark",
                name="Creative Inspiration",
                drone="loki",
                prompt="Offer a creative challenge or artistic inspiration that matches the current season and time of day.",
                time_segments=[TimeSegment.EVENING, TimeSegment.WORKDAY],
                automation_type=AutomationType.PROACTIVE,
                cooldown_hours=48,
            ),
            "wisdom_reflection": ProactiveAutomation(
                id="wisdom_reflection",
                name="Evening Reflection",
                drone="mimir",
                prompt="Provide a thoughtful reflection prompt for the day and intention-setting for tomorrow's growth.",
                time_segments=[TimeSegment.EVENING],
                automation_type=AutomationType.PROACTIVE,
                cooldown_hours=20,
            ),
            "weekend_adventure": ProactiveAutomation(
                id="weekend_adventure",
                name="Weekend Mischief",
                drone="luci",
                prompt="It's the weekend! Suggest something spontaneous, fun, and slightly mischievous to do in Toronto.",
                time_segments=[TimeSegment.MORNING, TimeSegment.EVENING],
                automation_type=AutomationType.PROACTIVE,
                cooldown_hours=48,
            ),
        }

    def get_pending_automations(self, context: AutomationContext) -> List[ProactiveAutomation]:
        """Get automations ready to trigger for current context"""
        pending = []

        for automation in self.automations.values():
            if automation.can_trigger(context):
                # Weekend filter for weekend_adventure
                if automation.id == "weekend_adventure" and not context.is_weekend:
                    continue

                pending.append(automation)

        return pending

    def mark_triggered(self, automation_id: str, triggered_time: datetime):
        """Mark automation as triggered"""
        if automation_id in self.automations:
            self.automations[automation_id].last_triggered = triggered_time
            logger.info(f"Marked automation {automation_id} as triggered at {triggered_time}")

    def toggle_automation(self, automation_id: str, enabled: bool) -> bool:
        """Enable/disable specific automation"""
        if automation_id in self.automations:
            self.automations[automation_id].enabled = enabled
            logger.info(f"Automation {automation_id} {'enabled' if enabled else 'disabled'}")
            return True
        return False

    def get_next_automation(self, context: AutomationContext) -> Optional[Tuple[ProactiveAutomation, datetime]]:
        """Get the next scheduled automation"""
        next_automation = None
        next_time = None

        # Calculate next trigger times for each automation
        for automation in self.automations.values():
            if not automation.enabled:
                continue

            # Find next time segment this automation should run
            for time_segment in automation.time_segments:
                next_trigger = self._calculate_next_trigger(context.current_time, time_segment)

                # Check if automation can run at that time
                if automation.last_triggered:
                    time_since = next_trigger - automation.last_triggered
                    if time_since.total_seconds() < (automation.cooldown_hours * 3600):
                        continue

                if next_time is None or next_trigger < next_time:
                    next_time = next_trigger
                    next_automation = automation

        return (next_automation, next_time) if next_automation else None

    def _calculate_next_trigger(self, current_time: datetime, time_segment: TimeSegment) -> datetime:
        """Calculate next trigger time for a time segment"""
        segment_hours = {
            TimeSegment.EARLY_MORNING: 6,
            TimeSegment.MORNING: 8,
            TimeSegment.WORKDAY: 13,  # 1 PM for midday
            TimeSegment.EVENING: 18,  # 6 PM
            TimeSegment.NIGHT: 21,  # 9 PM
        }

        target_hour = segment_hours[time_segment]

        # Calculate next occurrence
        next_time = current_time.replace(hour=target_hour, minute=0, second=0, microsecond=0)

        # If time has passed today, move to tomorrow
        if next_time <= current_time:
            next_time += timedelta(days=1)

        return next_time

    def get_automation_status(self) -> Dict:
        """Get current automation system status"""
        context = self.get_current_context()
        pending = self.get_pending_automations(context)
        next_automation = self.get_next_automation(context)

        return {
            "context": context.to_dict(),
            "pending_count": len(pending),
            "pending_automations": [
                {"id": auto.id, "name": auto.name, "drone": auto.drone, "type": auto.automation_type.value}
                for auto in pending
            ],
            "next_automation": (
                {
                    "name": next_automation[0].name,
                    "drone": next_automation[0].drone,
                    "scheduled_time": next_automation[1].isoformat(),
                    "time_until": str(next_automation[1] - context.current_time),
                }
                if next_automation
                else None
            ),
            "total_automations": len(self.automations),
            "enabled_automations": len([a for a in self.automations.values() if a.enabled]),
        }
