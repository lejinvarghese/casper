from llama_index.core.memory import ChatMemoryBuffer
from src.models import EmbeddingModel, InstructModel
from src.storage import Storage
from src.utils.logger import StreamingLogger
from src.prompts import personas

logger = StreamingLogger(__name__)
llm = InstructModel()
emb = EmbeddingModel()
index = Storage(llm=llm.model, embed_model=emb.model).load_vector_index()
memory = ChatMemoryBuffer.from_defaults(token_limit=7200)

default_chat_engine = index.as_chat_engine(
    chat_mode="simple", memory=memory, verbose=True
)


class ChatEngine:
    def __init__(
        self,
        index_name: str = "research",
        chat_mode: str = "simple",
        verbose: bool = False,
        **kwargs,
    ):
        self.index = self._load_index(index_name)
        self.chat_mode = chat_mode
        self.persona = kwargs.get("persona", "casper")
        self.verbose = verbose
        self.engine = self._get_engine()

    def _load_index(self, index_name: str):
        """Load the appropriate index based on the index_name."""
        storage = Storage(llm=llm.model, embed_model=emb.model)
        if index_name == "research":
            return storage.load_research_index()
        return storage.load_vector_index()

    def _get_engine(self):
        """Initialize the chat engine."""
        return self.index.as_chat_engine(
            chat_mode=self.chat_mode,
            verbose=self.verbose,
            system_prompt=personas.get(self.persona),
        )

    def chat(self, user_query: str) -> str:
        return self.engine.chat(user_query)

    def update_engine(self, chat_mode: str = None, persona: str = None):
        """Update configuration dynamically."""
        if chat_mode:
            self.chat_mode = chat_mode
        if persona:
            if persona in personas:
                self.persona = persona
            else:
                logger.warning(f"Persona {persona} not found. Using default persona.")
                self.persona = "casper"
        self.engine = self._get_engine()
        return self


def main():
    while True:
        logger.debug("Enter your query:\n")
        user_query = input()

        response = default_chat_engine.stream_chat(user_query)
        for r in response.response_gen:
            logger.info(r)
        logger.flush()


if __name__ == "__main__":
    main()
