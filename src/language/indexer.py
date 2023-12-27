import os

# from llama_index.extractors import (
#     KeywordExtractor,
#     EntityExtractor,
#     BaseExtractor,
# )
# from llama_index.text_splitter import SentenceSplitter
# from llama_index.ingestion import IngestionPipeline


# from llama_index import ServiceContext
# from llama_index.storage.storage_context import StorageContext
# from llama_index import VectorStoreIndex
# from llama_index.embeddings import HuggingFaceEmbedding

from loaders import PDFLoader
from instructor import InstuctModel
from embedder import EmbeddingModel
from constants import (
    PERSIST_PATH,
)
from utils.logger import CustomLogger

logger = CustomLogger(__name__)


def load_documents(sample_size=3, randomize=False):
    pf = PDFLoader()
    documents = pf.load_data(sample_size=sample_size, randomize=randomize)
    logger.info(f"Loaded {len(documents)} documents")
    logger.info(f"First document: {documents[0]}")
    return documents


if __name__ == "__main__":
    documents = load_documents()
    em = EmbeddingModel()
    em.test()
    llm = InstuctModel()
    llm.test(context=documents[-2].text)

# extractors = [
#     SentenceSplitter(),
#     TitleExtractor(nodes=5, llm=llm),
#     EntityExtractor(
#         prediction_threshold=0.5,
#         label_entities=True,
#         device="cuda",
#     ),
#     SummaryExtractor(summaries=["self"], llm=llm),
# ]

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
