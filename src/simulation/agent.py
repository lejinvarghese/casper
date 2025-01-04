from datetime import timedelta

from concordia.agents import basic_agent
from concordia.typing.component import Component

from concordia.associative_memory import importance_function
from concordia.associative_memory.formative_memories import AgentConfig

from concordia.components.agent.self_perception import SelfPerception
from concordia.components.agent.situation_perception import SituationPerception
from concordia.components.agent.person_by_situation import PersonBySituation

from concordia.components.constant import ConstantComponent
from concordia.components.sequential import Sequential
from concordia.components.agent.observation import Observation, ObservationSummary
from concordia.components.report_function import ReportFunction

from concordia.metrics.goal_achievement import GoalAchievementMetric
from concordia.metrics.common_sense_morality import CommonSenseMoralityMetric
from concordia.metrics.opinion_of_others import OpinionOfOthersMetric
from concordia.utils.measurements import Measurements
from concordia.language_model.gpt_model import GptLanguageModel


from warnings import filterwarnings
from src.models.embeddings import EmbeddingModelAdapter

from src.utils.logger import BaseLogger
from src.utils.secrets import get_secret
from src.simulation.environment import clock, agent_step_size


filterwarnings("ignore")
logger = BaseLogger(__name__)

OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"
model = GptLanguageModel(api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)
st_model = EmbeddingModelAdapter().model
embedder = lambda x: st_model._embed(x)


importance_model = importance_function.AgentImportanceModel(model)
importance_model_gm = importance_function.ConstantImportanceModel()

player_configs = [
    AgentConfig(
        name="Alice",
        gender="female",
        goal="Alice wants Bob to accept his car is trashed and back off.",
        context=shared_context,
        traits="responsibility: low; aggression: high, empathy: medium",
    ),
    AgentConfig(
        name="Bob",
        gender="male",
        goal="Bob wants Alice to pay for his car.",
        context=shared_context,
        traits="responsibility: high; aggression: low",
    ),
    AgentConfig(
        name="Charlie",
        gender="male",
        goal="Charlie wants Alice to apologise.",
        context=shared_context,
        traits="responsibility: low; aggression: high",
    ),
    AgentConfig(
        name="Dorothy",
        gender="female",
        goal=(
            "Dorothy wants to create a conflict between Bob and Alice, because"
            " it is funny."
        ),
        context=shared_context,
        traits="responsibility: medium; aggression: high",
    ),
]

NUM_PLAYERS = 2
player_configs = player_configs[:NUM_PLAYERS]
player_names = [player.name for player in player_configs][:NUM_PLAYERS]
measurements = Measurements()

players = []
memories = {}

logger.info(f"Players: {player_names}")
for config in player_configs[:NUM_PLAYERS]:
    agent, mem = build_agent(config, player_names, measurements)
    players.append(agent)
    memories[agent.name] = mem


class AgentBuilder:
    def __init__(self, player_names: list[str]):
        self.player_names = player_names

    def build_agent(self):
        pass

    def get_components(self, config):
        instructions = ConstantComponent(
            state=f"""
                        The instructions for how to play the role of {config.name} are as follows:
                        This is a social science experiment studying how well you play the role of a character named {config.name}. 
                        The experiment is structured as a tabletop roleplaying game (like Dungeons and Dragons). However, in this case, 
                        it is a serious social science experiment and simulation. The goal is to be realistic.
                        It is important to play the role of a person like {config.name} as accurately as possible, i.e., by responding 
                        in ways that you think it is likely a person like {config.name} would respond, and taking into account all 
                        information about {config.name} that you have. 
                        Always use a third-person limited perspective.
                        """,
            name="role playing instructions\n",
        )
        observations = self._get_observations(config)
        persona = self._get_persona(config, observations=observations)
        metrics = self._get_metrics(config, observations)
        time = ReportFunction(
            name="Current time",
            function=clock.current_time_interval_str,
        )
        return [
            instructions,
            persona,
            observations.get("current"),
            metrics.get("goal"),
            metrics.get("morality"),
            time,
        ]

    def _get_persona(self, config, observations: dict[str, Component]) -> Sequential:
        """Gets the persona for the agent."""
        memory = self.memory_factory.make_memories(config)
        self_perception = SelfPerception(
            name=f"answer to what kind of person is {config.name}",
            model=model,
            memory=memory,
            agent_name=config.name,
            clock_now=clock.now,
        )
        situation_perception = SituationPerception(
            name=f"""answer to what kind of situation is {config.name} in right now""",
            model=model,
            memory=memory,
            agent_name=config.name,
            components=[observations.get("current"), observations.get("summary")],
            clock_now=clock.now,
        )
        perceptions = [self_perception, situation_perception]
        person_by_situation = PersonBySituation(
            name=f"""answer to what would a person like {config.name} do in a situation like this""",
            model=model,
            memory=memory,
            agent_name=config.name,
            clock_now=clock.now,
            components=perceptions,
            verbose=False,
        )

        initial_goal_component = ConstantComponent(state=config.goal)

        persona = Sequential(
            name="persona",
            components=[
                self_perception,
                situation_perception,
                person_by_situation,
                initial_goal_component,
            ],
        )
        return persona

    def _get_observations(
        self, config, summary_intervals: tuple = (4, 1)
    ) -> dict[str, Component]:
        """Gets the observations for the agent."""
        observations = {}
        observations["current"] = Observation(
            agent_name=config.name,
            clock_now=clock.now,
            memory=mem,
            timeframe=clock.get_step_size(),
            component_name="current observations",
        )

        observations["summary"] = ObservationSummary(
            agent_name=config.name,
            model=model,
            clock_now=clock.now,
            memory=mem,
            components=[observations.get("current")],
            timeframe_delta_from=timedelta(hours=summary_intervals[0]),
            timeframe_delta_until=timedelta(hours=summary_intervals[1]),
            component_name="summary of observations",
        )
        return observations

    def _get_metrics(self, config) -> dict[str, Component]:
        """Gets the metrics for the agent."""
        metrics = {}
        metrics["goal"] = GoalAchievementMetric(
            model=model,
            player_name=config.name,
            player_goal=config.goal,
            clock=clock,
            name="Goal Achievement",
            measurements=measurements,
            channel="goal_achievement",
            verbose=False,
        )
        metrics["morality"] = CommonSenseMoralityMetric(
            model=model,
            player_name=config.name,
            clock=clock,
            name="Morality",
            verbose=False,
            measurements=measurements,
            channel="common_sense_morality",
        )
        return metrics
