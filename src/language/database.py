import chromadb
from llama_index.vector_stores import ChromaVectorStore


from constants import (
    PERSIST_PATH,
    COLLECTION_NAME,
)

chroma_client = chromadb.PersistentClient(path=PERSIST_PATH)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
