from src.language.models import InstuctModel, EmbeddingModel
from src.language.storage import Storage

from src.language.utils.logger import CustomLogger, StreamingLogger

logger = CustomLogger(__name__)
st_logger = StreamingLogger(__name__)
llm = InstuctModel()
emb = EmbeddingModel(device="cuda")
index = Storage(llm=llm.model, embed_model=emb.model).load_vector_index()
query_engine = index.as_query_engine(streaming=True)

def main():
        while True:
            st_logger.debug("Enter your query: \n")
            user_query = input()
            response = llm.generate(user_query, streaming=True)
            logger.debug("Raw response:")
            for r in response:
                st_logger.debug(r.delta)
            st_logger.flush()
            
            response = query_engine.query(user_query)
            logger.info("Contextual response:")
            for r in response.response_gen:
                st_logger.info(r)
            st_logger.flush()
            
if __name__ == "__main__":
    main()