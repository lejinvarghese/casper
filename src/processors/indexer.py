import asyncio

from src.processors.extractor import Pipeline
from src.processors.loaders import PDFLoader
from src.models.completion import MistralModelAdapter
from src.models.embeddings import EmbeddingModelAdapter
from src.storage import Storage
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)

llm = MistralModelAdapter().model
emb = EmbeddingModelAdapter(batch_size=32, device="cpu").model
st = Storage(llm=llm, embed_model=emb)
p = Pipeline(llm=llm, embed_model=emb, storage=st)


def load_documents(sample_size=None, randomize=False):
    pf = PDFLoader()
    documents = pf.load_data(sample_size=sample_size, randomize=randomize)
    logger.info(f"First document: {documents[0]}")
    return documents


async def main():
    documents = load_documents()
    nodes = await p.run(documents=documents)
    st.create_vector_index(nodes=nodes)


if __name__ == "__main__":
    asyncio.run(main())
