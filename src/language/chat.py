from src.language.models import InstuctModel, EmbeddingModel
from src.language.storage import Storage

from src.language.utils.logger import CustomLogger

logger = CustomLogger(__name__)
llm = InstuctModel()
emb = EmbeddingModel(device="cuda")
st = Storage(llm=llm.model, embed_model=emb.model)
index = st.load_vector_index()
query_engine = index.as_query_engine()

def main():
        while True:
            query_str = input("Enter your query: ")
            response = llm.generate(query_str)
            logger.debug(f"Raw response: {str(response)}")

            response = query_engine.query(query_str)
            logger.info(f"Contextual response: {str(response)}")

if __name__ == "__main__":
    main()