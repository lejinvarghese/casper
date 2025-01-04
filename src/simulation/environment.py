from datetime import datetime, timedelta
from concordia.clocks.game_clock import MultiIntervalClock

interval = 10
agent_step_size = timedelta(minutes=10)
step_sizes = [agent_step_size, timedelta(seconds=interval)]

setup_time = datetime.now()
clock = MultiIntervalClock(start=setup_time, step_sizes=step_sizes)
start_time = setup_time + timedelta(minutes=1)
