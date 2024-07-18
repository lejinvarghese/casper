import os
from typing import Dict, List, Sequence

from llama_index.async_utils import run_jobs
from llama_index.bridge.pydantic import Field
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.extractors import BaseExtractor, EntityExtractor, KeywordExtractor
from llama_index.ingestion import IngestionPipeline
from llama_index.llm_predictor.base import LLMPredictorType
from llama_index.prompts import PromptTemplate
from llama_index.schema import BaseNode, Document, TextNode
from llama_index.text_splitter import SentenceSplitter
from src.constants import NUM_WORKERS, PERSIST_DIR, SUMMARIZATION_PROMPT
from src.storage import Storage
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)
os.environ["TOKENIZERS_PARALLELISM"] = "true"


class CustomTitleExtractor(BaseExtractor):
    llm: LLMPredictorType = Field(description="The LLM to use for generation.")
    prompt: PromptTemplate = Field(
        description="The prompt to extract titles with.",
    )

    def __init__(
        self,
        llm: LLMPredictorType,
        prompt: PromptTemplate,
        num_workers: int = NUM_WORKERS,
    ):
        super().__init__(
            llm=llm,
            prompt=PromptTemplate(template=prompt),
            num_workers=num_workers,
        )

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        jobs = [self.llm.apredict(self.prompt, context_str=node.text) for node in nodes]
        tasks = await run_jobs(jobs, show_progress=self.show_progress)
        return [{"node_title": t.strip(' \t\n\r"')} for t in tasks]


class Pipeline:
    def __init__(
        self,
        llm: LLMPredictorType = None,
        embed_model: HuggingFaceEmbedding = None,
        prompt: PromptTemplate = SUMMARIZATION_PROMPT,
        chunk_size: int = 512,
        chunk_overlap: int = 16,
        prediction_threshold: float = 0.6,
        label_entities: bool = False,
        keywords: int = 5,
        storage: Storage = None,
        num_workers: int = NUM_WORKERS,
    ):
        self.num_workers = num_workers
        self.transformations = [
            SentenceSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ),
            EntityExtractor(
                prediction_threshold=prediction_threshold,
                label_entities=label_entities,
                device="cuda",
                num_workers=self.num_workers,
            ),
            KeywordExtractor(keywords=keywords, llm=llm, num_workers=self.num_workers),
            CustomTitleExtractor(
                llm=llm,
                prompt=prompt,
                num_workers=self.num_workers,
            ),
        ]
        self.storage = storage
        self.embed_model = embed_model
        self.__setup_pipeline()

    async def run(
        self,
        documents: List[Document],
    ) -> List[TextNode]:
        nodes = await self._extract_metadata(documents=documents)
        nodes = self._extract_embeddings(nodes)
        self.pipeline.persist(PERSIST_DIR)
        logger.info(f"Ingested {len(nodes)} nodes")
        return nodes

    async def _extract_metadata(self, documents: List[Document], verbose: bool = True) -> List[TextNode]:
        return await self.pipeline.arun(documents=documents, show_progress=verbose)

    def _extract_embeddings(self, nodes: List[TextNode]) -> List[TextNode]:
        for node in nodes:
            node.metadata["entities"] = ", ".join(node.metadata.get("entities", []))
            node.embedding = self.embed_model.get_text_embedding(node.get_content(metadata_mode="all"))
        return nodes

    def __setup_pipeline(self) -> None:
        self.pipeline = IngestionPipeline(transformations=self.transformations, docstore=self.storage.docstore)
        try:
            self.pipeline.load(PERSIST_DIR)
        except FileNotFoundError:
            pass
