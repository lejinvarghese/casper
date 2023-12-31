from src.language.models import InstuctModel, EmbeddingModel
from src.language.storage import Storage

from src.language.utils.logger import BaseLogger, StreamingLogger

base_logger = BaseLogger(__name__)
streaming_logger = StreamingLogger(__name__)
llm = InstuctModel()
emb = EmbeddingModel()
index = Storage(llm=llm.model, embed_model=emb.model).load_vector_index()
query_engine = index.as_query_engine(streaming=True)

def main():
        while True:
            streaming_logger.debug("Enter your query: \n")
            user_query = input()
            response = llm.generate(user_query, streaming=True)
            base_logger.debug("Raw response:")
            for r in response:
                streaming_logger.debug(r.delta)
            streaming_logger.flush()
            
            response = query_engine.query(user_query)
            base_logger.info("Contextual response:")
            for r in response.response_gen:
                streaming_logger.info(r)
            streaming_logger.flush()
            
if __name__ == "__main__":
    main()