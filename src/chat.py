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
        if index_name == "research":
            self.index = Storage(
                llm=llm.model, embed_model=emb.model
            ).load_research_index()
        else:
            self.index = Storage(
                llm=llm.model, embed_model=emb.model
            ).load_vector_index()
        self.engine = self.index.as_chat_engine(
            chat_mode=chat_mode,
            verbose=verbose,
            system_prompt=kwargs.get("persona", personas.get("casper", "")),
        )

    def chat(self, user_query: str) -> str:
        return self.engine.chat(user_query)


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
