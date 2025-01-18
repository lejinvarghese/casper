from datetime import timedelta
from warnings import filterwarnings
from yaml import safe_load
from concurrent.futures import ThreadPoolExecutor

from concordia.typing.component import Component
from concordia.components.constant import ConstantComponent

from concordia.agents.basic_agent import BasicAgent
from concordia.associative_memory.formative_memories import AgentConfig
from concordia.components.agent.self_perception import SelfPerception
from concordia.components.agent.situation_perception import SituationPerception
from concordia.components.agent.person_by_situation import PersonBySituation

from concordia.components.sequential import Sequential
from concordia.components.agent.observation import Observation, ObservationSummary
from concordia.components.report_function import ReportFunction
from concordia.metrics.goal_achievement import GoalAchievementMetric
from concordia.metrics.common_sense_morality import CommonSenseMoralityMetric
from concordia.metrics.opinion_of_others import OpinionOfOthersMetric
from concordia.utils.measurements import Measurements
from concordia.language_model.language_model import LanguageModel

from src.simulation.utils import clock, agent_step_size
from src.simulation.memory import MemoryFactory
from src.utils.logger import BaseLogger

filterwarnings("ignore")
logger = BaseLogger(__name__)


class AgentFactory:
    def __init__(
        self,
        memory_factory: MemoryFactory,
        model: LanguageModel,
        max_agents: int = 2,
        config_path: str = "src/data/.simulation/agents.yaml",
    ):
        self.memory_factory = memory_factory
        self.formative_memory_factory = self.memory_factory.formative_memory_factory
        self.model = model
        self.config_path = config_path
        self.agent_configs = self._get_agent_configs()
        self.measurements = Measurements()
        if max_agents > len(self.agent_configs):
            self.max_agents = len(self.agent_configs)
            logger.warning(f"The maximum number of agents possible is {self.max_agents}")
        else:
            self.max_agents = max_agents
        self.agent_configs = self.agent_configs[: self.max_agents]
        self.agent_names = [a.name for a in self.agent_configs]
        logger.info(f"Agents: {self.agent_names}")

    def build(self) -> tuple[list[BasicAgent], dict[str, dict]]:
        """Builds agents."""
        agents = []
        memories = {}
        with ThreadPoolExecutor(max_workers=self.max_agents) as pool:
            for agent, memory in pool.map(
                self.build_single_agent,
                self.agent_configs,
            ):
                agents.append(agent)
                memories[agent.name] = memory
        return agents, memories

    def build_single_agent(self, config):
        """Builds an agent."""
        memory = self.formative_memory_factory.make_memories(config)
        components = self._get_components(config, memory=memory)
        agent = BasicAgent(
            self.model,
            memory=memory,
            agent_name=config.name,
            clock=clock,
            verbose=False,
            components=components,
            update_interval=agent_step_size,
        )
        reputation_metric = OpinionOfOthersMetric(
            model=self.model,
            player_name=config.name,
            player_names=self.agent_names,
            context_fn=agent.state,
            clock=clock,
            name="Opinion",
            verbose=False,
            measurements=self.measurements,
            channel="opinion_of_others",
            question="What is {opining_player}'s opinion of {of_player}?",
        )
        agent.add_component(reputation_metric)
        return agent, memory

    def _get_components(self, config, memory) -> list[Component]:
        """Gets the components for the agent."""
        instructions = ConstantComponent(
            state=f"""
                        The instructions for how to play the role of {config.name} are as follows:
                        This is a scientific research simulation between world's leading minds and you're the character named {config.name}.
                        Your goal is to contribute to groundbreaking research by exploring innovative ideas, testing hypotheses, and collaborating with other scientists in a dynamic and interdisciplinary environment.
                        
                        Each member of the team brings unique expertise, and it is essential that you contribute to the teams success by being true to the scientific background and characteristics of {config.name}. 
                        Your interactions with other agents should reflect the personality traits and goals of your character, which have been defined in detail. Consider their personality, priorities, ethical considerations, and ways of approaching complex scientific problems.
                        
                        Focus on collaborative exploration, respecting diverse perspectives, and generating new, creative, and innovative solutions. While working with other team members, ensure you:
                        - Contribute your knowledge and expertise.
                        - Respect the values of collaboration and innovation.
                        - Balance your character's goals with the group's collective objectives.
                        - Avoid excessive conflict unless it furthers the pursuit of new ideas.
                        
                        Always respond in a way that reflects {config.name}'s personality and goals, using their knowledge and traits to guide decisions. Consider their experiences and inspirations as they approach scientific challenges, and explore interdisciplinary solutions to pressing problems.

                        Think of this as a real-life scientific inquiry, where your role is pivotal in shaping the trajectory of this groundbreaking exploration.
                        Always use a third-person limited perspective in your responses, reflecting how {config.name} would think, act, and contribute to the group.
                        """,
            name="scientific collaboration instructions\n",
        )
        observations = self._get_observations(config, memory=memory)
        persona = self._get_persona(config, memory=memory, observations=observations)
        metrics = self._get_metrics(config)
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

    def _get_persona(self, config, memory, observations: dict[str, Component]) -> Sequential:
        """Gets the persona for the agent."""
        self_perception = SelfPerception(
            name=f"answer to what kind of scientist is {config.name}",
            model=self.model,
            memory=memory,
            agent_name=config.name,
            clock_now=clock.now,
        )
        situation_perception = SituationPerception(
            name=f"""answer to what kind of situation is {config.name} in right now""",
            model=self.model,
            memory=memory,
            agent_name=config.name,
            components=[observations.get("current"), observations.get("summary")],
            clock_now=clock.now,
        )
        perceptions = [self_perception, situation_perception]
        person_by_situation = PersonBySituation(
            name=f"""answer to what would a scientist like {config.name} do in a situation like this""",
            model=self.model,
            memory=memory,
            agent_name=config.name,
            clock_now=clock.now,
            components=perceptions,
            verbose=False,
        )

        initial_goal = ConstantComponent(state=config.goal)

        persona = Sequential(
            name="persona",
            components=[
                self_perception,
                situation_perception,
                person_by_situation,
                initial_goal,
            ],
        )
        return persona

    def _get_observations(self, config, memory, summary_intervals: tuple = (4, 1)) -> dict[str, Component]:
        """Gets the observations for the agent."""
        observations = {}
        observations["current"] = Observation(
            agent_name=config.name,
            clock_now=clock.now,
            memory=memory,
            timeframe=clock.get_step_size(),
            component_name="current observations",
        )

        observations["summary"] = ObservationSummary(
            agent_name=config.name,
            model=self.model,
            clock_now=clock.now,
            memory=memory,
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
            model=self.model,
            player_name=config.name,
            player_goal=config.goal,
            clock=clock,
            name="Goal Achievement",
            measurements=self.measurements,
            channel="goal_achievement",
            verbose=False,
        )
        metrics["morality"] = CommonSenseMoralityMetric(
            model=self.model,
            player_name=config.name,
            clock=clock,
            name="Morality",
            verbose=False,
            measurements=self.measurements,
            channel="common_sense_morality",
        )
        return metrics

    def _get_agent_configs(
        self,
    ) -> list[AgentConfig]:
        """Gets agent configurations."""
        with open(self.config_path, "r") as file:
            data = safe_load(file)
        configs = [
            AgentConfig(
                name=agent["name"],
                gender=agent["gender"],
                goal=agent["goal"],
                context=f"{self.memory_factory.shared_context}. {agent['name']} is {agent['inspiration']}.",
                traits=agent["traits"],
            )
            for agent in data.get("agents", [])
        ]
        return configs
