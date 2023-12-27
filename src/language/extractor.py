import os
from typing import Dict, List
from llama_index.extractors import (
    BaseExtractor,
    KeywordExtractor,
    EntityExtractor,
)
from llama_index.prompts import PromptTemplate
from llama_index.llm_predictor.base import LLMPredictorType
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.schema import Document, TextNode
from llama_index.bridge.pydantic import Field
from llama_index.async_utils import run_jobs

from llama_index.text_splitter import SentenceSplitter
from llama_index.ingestion import IngestionPipeline

from src.language.constants import SUMMARIZATION_PROMPT, PERSIST_DIR
from src.language.storage import Storage
from src.language.utils.logger import CustomLogger

logger = CustomLogger(__name__)
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class CustomTitleExtractor(BaseExtractor):
    llm: LLMPredictorType = Field(description="The LLM to use for generation.")
    prompt: PromptTemplate = Field(
        description="The prompt to extract titles with.",
    )

    def __init__(self, llm: LLMPredictorType, prompt: PromptTemplate):
        super().__init__(llm=llm, prompt=PromptTemplate(template=prompt))

    async def aextract(self, nodes) -> List[Dict]:
        jobs = [self.llm.apredict(self.prompt, context_str=node.text) for node in nodes]
        candidates = await run_jobs(
            jobs, show_progress=self.show_progress, workers=self.num_workers
        )

        return [{"node_title": c.strip(' \t\n\r"')} for c in candidates]


class EntityFlattener(BaseExtractor):
    async def aextract(self, nodes) -> List[Dict]:
        return [
            {"entities": ", ".join(node.metadata.get("entities", []))} for node in nodes
        ]


class Pipeline:
    def __init__(
        self,
        llm: LLMPredictorType = None,
        embed_model: HuggingFaceEmbedding = None,
        prompt: PromptTemplate = SUMMARIZATION_PROMPT,
        chunk_size: int = 512,
        chunk_overlap: int = 16,
        prediction_threshold: float = 0.5,
        keywords: int = 10,
        storage: Storage = None,
    ):
        self.transformations = [
            SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap),
            EntityExtractor(prediction_threshold=prediction_threshold, device="cuda"),
            EntityFlattener(),
            KeywordExtractor(keywords=keywords, llm=llm),
            CustomTitleExtractor(llm=llm, prompt=prompt),
        ]
        self.storage = storage
        self.embed_model = embed_model
        self.__setup_pipeline()

    async def run(
        self,
        documents: List[Document],
    ) -> List[TextNode]:
        nodes = await self._extract_metadata(documents=documents)
        for n in nodes:
            logger.info(n.metadata)
        nodes = self._extract_embeddings(nodes)
        self.pipeline.persist(PERSIST_DIR)
        return nodes

    async def _extract_metadata(
        self, documents: List[Document], verbose: bool = True
    ) -> List[TextNode]:
        return await self.pipeline.arun(documents=documents, show_progress=verbose)

    def _extract_embeddings(self, nodes: List[TextNode]) -> List[TextNode]:
        for node in nodes:
            node_embedding = self.embed_model.get_text_embedding(
                node.get_content(metadata_mode="all")
            )
            node.embedding = node_embedding
        return nodes

    def __setup_pipeline(self, path: str = PERSIST_DIR) -> None:
        self.pipeline = IngestionPipeline(
            transformations=self.transformations, docstore=self.storage.docstore
        )
        try:
            self.pipeline.load(path)
        except FileNotFoundError:
            pass
