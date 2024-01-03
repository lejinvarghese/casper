from typing import Dict, List

from chromadb import PersistentClient
from llama_index import ServiceContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llm_predictor.base import LLMPredictorType
from llama_index.schema import TextNode
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import ChromaVectorStore
from src.language.constants import COLLECTION_NAME, PERSIST_DIR


class Storage:
    def __init__(
        self,
        persist_directory: str = PERSIST_DIR,
        collection_name: str = COLLECTION_NAME,
        llm: LLMPredictorType = None,
        embed_model: HuggingFaceEmbedding = None,
    ):
        self.persist_directory = persist_directory
        try:
            self.docstore = SimpleDocumentStore.from_persist_dir(
                persist_dir=self.persist_directory
            )
        except FileNotFoundError:
            self.docstore = SimpleDocumentStore()
        self.chroma_client = PersistentClient(path=self.persist_directory)
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            collection_name
        )
        self.vector_store = ChromaVectorStore(
            chroma_collection=self.chroma_collection
        )
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store,
            docstore=self.docstore,
        )
        self.service_context = ServiceContext.from_defaults(
            llm=llm, embed_model=embed_model
        )

    def create_vector_index(self, nodes: List[TextNode]) -> None:
        index = VectorStoreIndex(
            nodes,
            storage_context=self.storage_context,
            service_context=self.service_context,
        )
        index.storage_context.persist(persist_dir=self.persist_directory)

    def load_vector_index(self) -> VectorStoreIndex:
        return VectorStoreIndex.from_vector_store(
            self.vector_store, self.service_context
        )
