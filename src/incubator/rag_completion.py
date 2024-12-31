from src.models.completion import MistralModelAdapter
from src.models.embeddings import EmbeddingModelAdapter
from src.storage import Storage
from src.utils.logger import StreamingLogger

logger = StreamingLogger(__name__)
llm = MistralModelAdapter()
emb = EmbeddingModelAdapter()
index = Storage(llm=llm.model, embed_model=emb.model).load_vector_index()
query_engine = index.as_query_engine(streaming=True)


def main():
    while True:
        logger.debug("Enter your query: \n")
        user_query = input()
        response = llm.generate(user_query, streaming=True)
        logger.debug("Natural response:")
        for r in response:
            logger.debug(r.delta)
        logger.flush()

        response = query_engine.query(user_query)
        logger.info("Augmented response:")
        try:
            for r in response.response_gen:
                logger.info(r)
        except Exception as e:
            logger.error(
                f"Error: Could not find an appropriate answer for your query: {e}"
            )
        logger.flush()


if __name__ == "__main__":
    main()
