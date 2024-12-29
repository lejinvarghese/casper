from llama_index.core.memory import ChatSummaryMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore

from src.models import EmbeddingModel, InstructModel
from src.storage import Storage
from src.utils.logger import StreamingLogger
from src.prompts import personas
from src.constants import PERSIST_DIR

logger = StreamingLogger(__name__)


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
        try:
            self.chat_store = SimpleChatStore.from_persist_path(
                persist_path=f"{PERSIST_DIR}/chat_store.json"
            )
        except Exception as e:
            logger.warning(f"Error loading chat store: {e}")
            self.chat_store = SimpleChatStore()
        self.buffer = ChatSummaryMemoryBuffer.from_defaults(
            token_limit=2048,
            chat_store_key=kwargs.get("user_id", ""),
            chat_store=self.chat_store,
        )
        self.engine = self._get_engine()

    def _load_index(self, index_name: str):
        """Load the appropriate index based on the index_name."""
        llm = InstructModel().model
        emb = EmbeddingModel().model
        storage = Storage(llm=llm, embed_model=emb)
        if index_name == "research":
            return storage.load_research_index()
        return storage.load_vector_index()

    def _get_engine(self):
        """Initialize the chat engine."""
        return self.index.as_chat_engine(
            chat_mode=self.chat_mode,
            verbose=self.verbose,
            system_prompt=personas.get(self.persona),
            memory=self.buffer,
        )

    def chat(self, user_query: str) -> str:
        response = self.engine.chat(user_query)
        self.chat_store.persist(persist_path=f"{PERSIST_DIR}/chat_store.json")
        return str(response)

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
    llm = InstructModel()
    emb = EmbeddingModel()
    index = Storage(llm=llm.model, embed_model=emb.model).load_vector_index()
    buffer = ChatSummaryMemoryBuffer.from_defaults(token_limit=2048)

    chat_engine = index.as_chat_engine(chat_mode="simple", memory=buffer, verbose=True)
    while True:
        logger.debug("Enter your query:\n")
        user_query = input()

        response = chat_engine.stream_chat(user_query)
        for r in response.response_gen:
            logger.info(r)
        logger.flush()


if __name__ == "__main__":
    main()
