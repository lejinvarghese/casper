from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from src.models import EmbeddingModel, InstructModel
from src.constants import RESEARCH_DIR

# llm = InstructModel().model
# emb = EmbeddingModel().model
Settings.llm = InstructModel().model
Settings.embed_model = EmbeddingModel().model

reader = SimpleDirectoryReader(input_dir=RESEARCH_DIR, exclude_hidden=False)
documents = reader.load_data()
print(len(documents))
print(documents[0])

index = VectorStoreIndex.from_documents(documents, )
chat_engine = index.as_chat_engine(chat_mode="condense_plus_context", verbose=True)

response = chat_engine.chat("Where was Lejin born?")
print(response)