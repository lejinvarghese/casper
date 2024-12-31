from chromadb import PersistentClient
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.llms import LLM
from llama_index.core.schema import TextNode
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

from src.utils.logger import BaseLogger
from src.constants import PERSIST_DIR, RESEARCH_DIR

logger = BaseLogger(__name__)


class Storage:
    def __init__(
        self,
        persist_directory: str = PERSIST_DIR,
        research_directory: str = RESEARCH_DIR,
        collection_name: str = "research",
        llm: LLM = None,
        embed_model: HuggingFaceEmbedding = None,
    ):
        self.persist_directory = persist_directory
        try:
            self.docstore = SimpleDocumentStore.from_persist_dir(
                persist_dir=self.persist_directory
            )
        except FileNotFoundError:
            logger.warning("Creating new document store")
            self.docstore = SimpleDocumentStore()
        self.research_docs = SimpleDirectoryReader(
            input_dir=research_directory, exclude_hidden=False, recursive=True
        ).load_data()
        self.chroma_client = PersistentClient(path=self.persist_directory)
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            collection_name
        )
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store,
            docstore=self.docstore,
        )
        Settings.llm = llm
        Settings.embed_model = embed_model
        Settings.chunk_size = 512
        Settings.chunk_overlap = 20

    def create_vector_index(self, nodes: list[TextNode]) -> None:
        index = VectorStoreIndex(
            nodes,
            storage_context=self.storage_context,
        )
        index.storage_context.persist(persist_dir=self.persist_directory)

    def load_vector_index(self) -> VectorStoreIndex:
        return VectorStoreIndex.from_vector_store(self.vector_store)

    def load_research_index(self) -> VectorStoreIndex:
        return VectorStoreIndex.from_documents(
            self.research_docs, storage_context=self.storage_context
        )
