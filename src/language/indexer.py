import os
from llama_index.readers import PDFReader
from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)

from llama_index.extractors import (
    KeywordExtractor,
    EntityExtractor,
    BaseExtractor,
)
from llama_index.text_splitter import SentenceSplitter
from llama_index.ingestion import IngestionPipeline


from llama_index import ServiceContext
from llama_index.storage.storage_context import StorageContext
from llama_index import VectorStoreIndex
import chromadb
from llama_index.vector_stores import ChromaVectorStore
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.prompts import PromptTemplate

from loaders import PDFLoader
from constants import (
    ARXIV_PATH,
    PERSIST_PATH,
    COLLECTION_NAME,
    INSTRUCTION_MODEL,
    EMBEDDING_MODEL,
)
from utils.logger import CustomLogger

logger = CustomLogger(__name__)

if __name__ == "__main__":
    pf = PDFLoader(ARXIV_PATH)
    documents = pf.load_data(sample_size=3, randomize=True)
    logger.info(f"Loaded {len(documents)} documents")
    logger.info(f"First document: {documents[0]}")


# llm = LlamaCPP(
#     model_path=MODEL_PATH,
#     temperature=0.1,
#     max_new_tokens=256,
#     context_window=3000,
#     generate_kwargs={},
#     model_kwargs={"n_gpu_layers": 30},
#     messages_to_prompt=messages_to_prompt,
#     completion_to_prompt=completion_to_prompt,
#     verbose=False,
# )

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
