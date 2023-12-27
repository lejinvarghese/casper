import asyncio

from src.language.loaders import PDFLoader
from src.language.models import InstuctModel, EmbeddingModel
from src.language.extractor import Pipeline
from src.language.storage import Storage
from src.language.utils.logger import CustomLogger

logger = CustomLogger(__name__)

llm = InstuctModel()
emb = EmbeddingModel(device="cpu")
st = Storage(llm=llm.model, embed_model=emb.model)
p = Pipeline(llm=llm.model, embed_model=emb.model, storage=st)


def load_documents(sample_size=3, randomize=False):
    pf = PDFLoader()
    documents = pf.load_data(sample_size=sample_size, randomize=randomize)
    logger.info(f"First document: {documents[0]}")
    return documents


async def main():
    documents = load_documents(sample_size=6)
    nodes = await p.run(documents=documents)
    index = st.create_vector_index(nodes=nodes)

    query_str = "Does emergence in LLMs really happen and when?"
    response = llm.generate(query_str)
    logger.warning(f"Raw response: {str(response)}")

    query_engine = index.as_query_engine()
    response = query_engine.query(query_str)
    logger.info(f"Contextual response: {str(response)}")


if __name__ == "__main__":
    asyncio.run(main())
