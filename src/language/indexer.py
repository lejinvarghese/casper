import asyncio

from src.language.loaders import PDFLoader
from src.language.models import InstuctModel, EmbeddingModel
from src.language.extractor import Pipeline
from src.language.storage import Storage
from src.language.utils.logger import BaseLogger

logger = BaseLogger(__name__)

llm = InstuctModel()
emb = EmbeddingModel(batch_size=32, device="cpu")
st = Storage(llm=llm.model, embed_model=emb.model)
p = Pipeline(llm=llm.model, embed_model=emb.model, storage=st)


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
