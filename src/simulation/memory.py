from concordia.associative_memory.blank_memories import MemoryFactory as BlankMemoryFactory
from concordia.associative_memory.formative_memories import FormativeMemoryFactory
from concordia.associative_memory.associative_memory import AssociativeMemory
from concordia.associative_memory.importance_function import (
    AgentImportanceModel,
    ConstantImportanceModel,
)
from src.simulation.utils import clock


class MemoryFactory:
    def __init__(self, model, embedder, topic):
        self.model = model
        self.embedder = embedder
        self.topic = topic

    @property
    def shared_memories(self):
        return [
            "There is a research facility on a remote island called Quarks, dedicated to groundbreaking experimental interdisciplinary research across scientific fields.",
            "Quarks is not just a state of the art research facility with advanced laboratories, it has beautiful galleries, bars, theatres, gardens with flora and fauna from across the world, and a library with rare manuscripts.",
            "The facility is designed to foster creativity, with endless avenues for both intellectual exploration and leisure, offering scenic views and quiet spaces for reflection.",
            "Quarks is a place where the research team thrives, not just in their scientific endeavors but in the freedom to think, debate, and dream outside the confines of traditional boundaries.",
            "The team often gathers in the Reflection Gardens after breakthroughs, discussing new theories, or simply unwinding under the stars, where ideas evolve as naturally as the landscape around them.",
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
