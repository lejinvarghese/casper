from concordia.associative_memory.blank_memories import MemoryFactory
from concordia.associative_memory.formative_memories import FormativeMemoryFactory
from src.simulation.environment import clock


class Memory:
    def __init__(self, model, embedder, importance_model):
        self.model = model
        self.embedder = embedder
        self.importance_model = importance_model

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
            return self.model.sample_text(
                f"""Summarize the following passage in a concise and insightful fashion:\n {memories}\n Summary: """
            )

        @property
        def blank_memory_factory(self):
            return self.__get_blank_memories()

        @property
        def formative_memory_factory(self):
            return self.__get_formative_memories()

    def __get_blank_memories(self):
        return MemoryFactory(
            model=self.model,
            embedder=self.embedder,
            importance=self.importance_model.importance,
            clock_now=clock.now,
        )

    def __get_formative_memories(self):
        return FormativeMemoryFactory(
            model=self.model,
            shared_memories=self.shared_memories,
            blank_memory_factory_call=self.blank_memory_factory.make_blank_memory,
        )
