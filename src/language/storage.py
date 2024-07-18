from typing import Dict, List

from chromadb import PersistentClient
from llama_index import ServiceContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS as faiss
from llama_index.llm_predictor.base import LLMPredictorType
from llama_index.schema import TextNode
from llama_index.storage.docstore import SimpleDocumentStore
from datasets import load_dataset
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import ChromaVectorStore
from src.language.constants import COLLECTION_NAME, PERSIST_DIR, EMBEDDING_MODEL


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
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
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


class FaissVectorStore:
    def __init__(
        self,
        dataset_name: str = "m-ric/huggingface_doc",
    ):
        self.dataset = load_dataset(dataset_name, split="train")
        self.embed_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL, model_kwargs={"trust_remote_code": True}
        )
        self.db, self.sources = self.create()

    def __preprocess(self):
        source_docs = [
            Document(
                page_content=doc["text"],
                metadata={"source": doc["source"].split("/")[1]},
            )
            for doc in self.dataset
        ]
        docs = RecursiveCharacterTextSplitter(chunk_size=500).split_documents(
            source_docs
        )[:1000]
        return docs

    def create(self):
        docs = self.__preprocess()
        sources = list(set([doc.metadata["source"] for doc in docs]))
        db = faiss.from_documents(documents=docs, embedding=self.embed_model)
        return db, sources
