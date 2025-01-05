from concordia.associative_memory.blank_memories import MemoryFactory as BlankMemoryFactory
from concordia.associative_memory.formative_memories import FormativeMemoryFactory
from concordia.associative_memory.associative_memory import AssociativeMemory
from concordia.associative_memory.importance_function import (
    AgentImportanceModel,
    ConstantImportanceModel,
)
from src.simulation.utils import clock


class MemoryFactory:
    def __init__(self, model, embedder):
        self.model = model
        self.embedder = embedder

    @property
    def shared_memories(self):
        return [
            "There is a pub called The Sundrop Saloon.",
            "Alice stole Bob's car and crashed it.",
            "Alice, Bob, Charlie and Dorothy always spend their evenings at the Sundrop Saloon.",
        ]

    @property
    def shared_context(self):
        memories = "\n".join(self.shared_memories)
        return self.model.sample_text(f"""Summarize the following passage in a concise and insightful fashion:\n {memories}\n Summary: """)

    @property
    def importance_models(self):
        return self.__get_importance_models()

    @property
    def blank_memory_factory(self):
        return self.__get_blank_memories()

    @property
    def associative_memory_factory(self):
        return self.__get_associative_memory()

    @property
    def formative_memory_factory(self):
        return self.__get_formative_memories()

    def __get_importance_models(self):
        return {
            "agent": AgentImportanceModel(self.model),
            "game_master": ConstantImportanceModel(),
        }

    def __get_blank_memories(self):
        return BlankMemoryFactory(
            model=self.model,
            embedder=self.embedder,
            importance=self.importance_models.get("agent").importance,
            clock_now=clock.now,
        )

    def __get_formative_memories(self):
        return FormativeMemoryFactory(
            model=self.model,
            shared_memories=self.shared_memories,
            blank_memory_factory_call=self.blank_memory_factory.make_blank_memory,
        )

    def __get_associative_memory(self):
        return AssociativeMemory(
            sentence_embedder=self.embedder,
            importance=self.importance_models.get("game_master").importance,
            clock=clock.now,
        )
