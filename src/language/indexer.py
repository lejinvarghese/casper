import asyncio

from loaders import PDFLoader
from instructor import InstuctModel
from embedder import EmbeddingModel
from extractor import Pipeline
from utils.logger import CustomLogger

logger = CustomLogger(__name__)

llm = InstuctModel()
emb = EmbeddingModel(device="cpu")
p = Pipeline(llm=llm.model, embed_model=emb.model)


def load_documents(sample_size=3, randomize=False):
    pf = PDFLoader()
    documents = pf.load_data(sample_size=sample_size, randomize=randomize)
    logger.info(f"Loaded {len(documents)} documents")
    logger.info(f"First document: {documents[0]}")
    return documents


async def main():
    documents = load_documents(sample_size=6)
    nodes = await p.extract_metadata(documents=documents)
    for i, n in enumerate(nodes):
        logger.info(n.metadata)
    nodes = p.add_embeddings(nodes)
    p.persist()


if __name__ == "__main__":
    asyncio.run(main())
    # emb.test()
    # llm.test(context=documents[-2].text)


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
