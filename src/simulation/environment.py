from warnings import filterwarnings
from concordia.language_model.gpt_model import GptLanguageModel
from concordia.utils.html import PythonObjectToHTMLConverter, combine_html_pages, finalise_html

from src.utils.secrets import get_secret
from src.utils.logger import BaseLogger
from src.models.embeddings import EmbeddingModelAdapter
from src.simulation.agent import AgentFactory
from src.simulation.game_master import GameMasterFactory
from src.simulation.memory import MemoryFactory
from src.simulation.utils import clock, start_time

OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"
filterwarnings("ignore")
logger = BaseLogger(__name__)


class Environment:
    def __init__(self, max_agents: int = 3, episode_length: int = 5, topic: str = "network science"):
        self.max_agents = max_agents
        self.episode_length = episode_length
        self.topic = topic
        self.llm = GptLanguageModel(api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)
        self.memory_factory = self.__get_memory_factory()

        self.agent_factory = AgentFactory(memory_factory=self.memory_factory, model=self.llm, max_agents=self.max_agents)
        self.agents, self.agent_memories = self.agent_factory.build()

        self.game_master_factory = GameMasterFactory(memory_factory=self.memory_factory, agents=self.agents, model=self.llm)
        self.game_master, self.game_master_memories = self.game_master_factory.build()

        self.initial_states = [
            f"The research team has just gathered in the serene Reflection Gardens at Quarks, a place where past breakthroughs and new ideas often come to life.",
            "Today, they are tasked with the creation of sustainable solutions for {self.topic}. Each member brings a unique perspective, blending interdisciplinary expertise with a drive to push boundaries.",
            "The setting is calm, with soft winds rustling through the trees and distant views of the ocean, allowing the team to reflect deeply on the challenges ahead.",
            "While their minds are focused on the task at hand, moments of disagreement and different approaches to problem-solving are already emerging, signaling the need for delicate coordination.",
            f"As the team takes a moment to breathe, they know that in these gardens, their creativity can flourish, and the seeds of the next big scientific breakthrough in {self.topic} are ready to be planted."
        ]

    def run(self):
        clock.set(start_time)
        logger.info("Adding environment state into memory:\n")
        for state in self.initial_states:
            logger.info(state)
            self.game_master_memories.add(state)
            for agent in self.agents:
                agent.observe(state)

        for _ in range(self.episode_length):
            logger.info(f"\nEpisode: {_} {clock.now()}:\n")
            self.game_master.step()

        self.log()

    def __get_memory_factory(self):
        emb_model = EmbeddingModelAdapter().model
        embedder = lambda x: emb_model._embed(x)
        return MemoryFactory(model=self.llm, embedder=embedder, topic = self.topic)

    def log(self):
        memory = self.game_master._memory
        self.__log_csv(memory, "game_master")
        html_logs = []
        for agent in self.agents:
            name = agent.name
            memory = self.agent_memories[name]
            self.__log_csv(memory, name)
            html_logs.append(self.__summarize_memories(memory))
        self.__log_html(html_logs)

    def __log_csv(self, memory, name: str) -> None:
        data = memory.get_data_frame().drop(columns=["embedding"]).sort_values(["time", "importance"], ascending=True)
        timestamp = clock.now().strftime("%Y%m%d%H%M%S")
        file_name = f"./src/data/.simulation/logs/{timestamp}_{str.lower(name)}.csv"
        data.to_csv(file_name, index=False)

    def __log_html(self, logs) -> None:
        timestamp = clock.now().strftime("%Y%m%d%H%M%S")
        file_name = f"./src/data/.simulation/logs/{timestamp}_summary.html"
        html = finalise_html(
            combine_html_pages(
                logs,
                [a.name for a in self.agents],
                summary="",
                title="Agent Memories",
            )
        )
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(html)

    def __summarize_memories(self, memory, k: int = 1000) -> str:
        recent_memory = memory.retrieve_recent(k=k, add_time=True)
        recent_memory_str = "\n".join(recent_memory)
        summary = self.llm.sample_text(
            f"""Sequence of events: {recent_memory_str}. Narratively summarize the above temporally ordered sequence of events. Summary: """,
            max_tokens=3500,
            terminators=(),
        )
        total_memory = ["Summary:", summary, "Memories:"] + recent_memory
        return PythonObjectToHTMLConverter(total_memory).convert()
