import chromadb
from llama_index import ServiceContext
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index import VectorStoreIndex


from constants import (
    PERSIST_PATH,
    COLLECTION_NAME,
)

chroma_client = chromadb.PersistentClient(path=PERSIST_PATH)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

storage_context = StorageContext.from_defaults(
    vector_store=vector_store,
)
# service_context = ServiceContext.from_defaults(llm=llm.model, embed_model=emb.model)
# index = VectorStoreIndex(
#     nodes, storage_context=storage_context, service_context=service_context
# )
