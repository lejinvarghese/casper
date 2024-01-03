from src.language.models import InstuctModel, EmbeddingModel
from src.language.storage import Storage

from src.language.utils.logger import StreamingLogger

logger = StreamingLogger(__name__)
llm = InstuctModel()
emb = EmbeddingModel()
index = Storage(llm=llm.model, embed_model=emb.model).load_vector_index()
chat_engine = index.as_chat_engine(chat_mode="condense_plus_context", verbose=False)


def main():
    while True:
        logger.debug("Enter your query: \n")
        user_query = input()

        response = chat_engine.stream_chat(user_query)
        for r in response.response_gen:
            logger.info(r)
        logger.flush()


if __name__ == "__main__":
    main()
