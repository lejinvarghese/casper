from datasets import load_dataset
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import json
from transformers.agents import Tool
from transformers.agents import HfEngine, ReactJsonAgent
from langchain_core.vectorstores import VectorStore
from warnings import filterwarnings

from src.language.utils.logger import BaseLogger

logger = BaseLogger(__name__)
filterwarnings("ignore")

knowledge_base = load_dataset("m-ric/huggingface_doc", split="train")
source_docs = [
    Document(page_content=doc["text"], metadata={"source": doc["source"].split("/")[1]})
    for doc in knowledge_base
]

docs_processed = RecursiveCharacterTextSplitter(chunk_size=500).split_documents(
    source_docs
)[:1000]

embedding_model = HuggingFaceEmbeddings(
    model_name="thenlper/gte-small", model_kwargs={"trust_remote_code": True}
)
vectordb = FAISS.from_documents(documents=docs_processed, embedding=embedding_model)
all_sources = list(set([doc.metadata["source"] for doc in docs_processed]))
logger.info(all_sources)


class RetrieverTool(Tool):
    name = "retriever"
    description = "Retrieves some documents from the knowledge base that have the closest embeddings to the input query."
    inputs = {
        "query": {
            "type": "text",
            "description": "The query to perform. This should be semantically close to your target documents. Use the affirmative form rather than a question.",
        },
        "source": {"type": "text", "description": ""},
    }
    output_type = "text"

    def __init__(self, vectordb: VectorStore, all_sources: str, **kwargs):
        super().__init__(**kwargs)
        self.vectordb = vectordb
        self.inputs["source"][
            "description"
        ] = f"The source of the documents to search, as a str representation of a list. Possible values in the list are: {all_sources}. If this argument is not provided, all sources will be searched."

    def forward(self, query: str, source: str = None) -> str:
        assert isinstance(query, str), "Your search query must be a string"

        if source:
            if isinstance(source, str) and "[" not in str(
                source
            ):  # if the source is not representing a list
                source = [source]
            source = json.loads(str(source).replace("'", '"'))

        docs = self.vectordb.similarity_search(
            query, filter=({"source": source} if source else None), k=3
        )

        if len(docs) == 0:
            return "No documents found with this filtering. Try removing the source filter."
        return "Retrieved documents:\n\n" + "\n===Document===\n".join(
            [doc.page_content for doc in docs]
        )


llm_engine = HfEngine("mistralai/Mixtral-8x7B-Instruct-v0.1")

agent = ReactJsonAgent(
    tools=[RetrieverTool(vectordb, all_sources)], llm_engine=llm_engine
)

agent_output = agent.run("Please show me a finetuning script")
logger.info(f"Final output: {agent_output}")
