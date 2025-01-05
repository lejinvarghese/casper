from datetime import datetime, timedelta
from concordia.clocks.game_clock import MultiIntervalClock
from src.utils.logger import BaseLogger
logger = BaseLogger(__name__)

interval = 10
agent_step_size = timedelta(minutes=10)
step_sizes = [agent_step_size, timedelta(seconds=interval)]

setup_time = datetime.now()
start_time = setup_time + timedelta(minutes=1)
clock = MultiIntervalClock(start=setup_time, step_sizes=step_sizes)

logger.info(f"Starting simulation at: {setup_time.strftime('%d %b %Y [%H:%M:%S]')}")
