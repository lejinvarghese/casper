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
    logger.info(f"Loaded {len(documents)} documents")
    logger.info(f"First document: {documents[0]}")
    return documents


async def main():
    documents = load_documents(sample_size=6)
    nodes = await p.run(documents=documents)
    logger.info(f"Ingested {len(nodes)} nodes")


if __name__ == "__main__":
    asyncio.run(main())


# try:
#     docstore = SimpleDocumentStore.from_persist_dir(persist_dir=STORAGE_PATH)
# except FileNotFoundError:
#     docstore = SimpleDocumentStore()


# pipeline = IngestionPipeline(
#     transformations=extractors,
#     docstore=docstore,
# )
# try:
#     pipeline.load(STORAGE_PATH)
# except FileNotFoundError:
#     pass

# nodes = pipeline.run(
#     documents=documents,
#     in_place=True,
#     show_progress=True,
# )
# pipeline.persist(STORAGE_PATH)
# logging.info(f"Ingested {len(nodes)} Nodes")
