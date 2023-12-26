import os
from llama_index.readers import PDFReader
import logging


from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from llama_index.extractors import (
    TitleExtractor,
    EntityExtractor,
    SummaryExtractor
)
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.ingestion import IngestionPipeline
from llama_index.text_splitter import SentenceSplitter


DOCUMENT_PATH = ".papers"
STORAGE_PATH = ".pipeline_storage"
QUANT_VERSION = "mistral-7b-instruct-v0.2.Q3_K_S.gguf"
MODEL_PATH = f"./models/{QUANT_VERSION}"

logging.basicConfig(level=logging.INFO)

files = os.listdir(DOCUMENT_PATH)
loader = PDFReader()

documents = []
for i in files:
    documents.append(loader.load_data(f".papers/{i}"))
    
documents = [c for d in documents for c in d]

logging.info(f"Loaded {len(documents)} documents")

llm = LlamaCPP(
    model_path=MODEL_PATH,
    temperature=0.1,
    max_new_tokens=256,
    context_window=3000,
    generate_kwargs={},
    model_kwargs={"n_gpu_layers": 30},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=False,
)

extractors = [
    SentenceSplitter(),
    TitleExtractor(nodes=5, llm=llm),
    EntityExtractor(
    prediction_threshold=0.5,
    label_entities=True, 
    device="cuda", 
),
    SummaryExtractor(summaries=[ "self"], llm=llm),
]

try:
    docstore = SimpleDocumentStore.from_persist_dir(persist_dir=STORAGE_PATH)
except FileNotFoundError:
    docstore = SimpleDocumentStore()


pipeline = IngestionPipeline(
    transformations=extractors,
    docstore=docstore,
)
try:
    pipeline.load(STORAGE_PATH)
except FileNotFoundError:
    pass

nodes = pipeline.run(
    documents=documents,
    in_place=True,
    show_progress=True,
)
pipeline.persist(STORAGE_PATH)
logging.info(f"Ingested {len(nodes)} Nodes")