import json
from PIL import Image
from io import BytesIO
from langchain_core.vectorstores import VectorStore
from transformers.agents import Tool


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

    def __init__(self, db: VectorStore, sources: str, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.inputs["source"][
            "description"
        ] = f"The source of the documents to search, as a str representation of a list. Possible values in the list are: {sources}. If this argument is not provided, all sources will be searched."

    def forward(self, query: str, source: str = None) -> str:
        assert isinstance(query, str), "Your search query must be a string"

        if source:
            if isinstance(source, str) and "[" not in str(
                source
            ):  # if the source is not representing a list
                source = [source]
            source = json.loads(str(source).replace("'", '"'))

        docs = self.db.similarity_search(
            query, filter=({"source": source} if source else None), k=3
        )

        if len(docs) == 0:
            return "No documents found with this filtering. Try removing the source filter."
        return "Retrieved documents:\n\n" + "\n===Document===\n".join(
            [doc.page_content for doc in docs]
        )
