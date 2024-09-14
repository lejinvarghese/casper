import os
import random

from llama_index.readers import PDFReader
from src.constants import PDF_DIR
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)


class PDFLoader:
    """
    A loader for PDF files.
    """

    def __init__(self, source_path: str = PDF_DIR):
        self._source_path = source_path
        self._files = os.listdir(self._source_path)
        self._loader = PDFReader()

    def load_data(
        self,
        sample_size: int = None,
        randomize: bool = False,
        random_seed: int = 42,
    ):
        documents = [
            self._loader.load_data(os.path.join(self._source_path, i))
            for i in self._files
        ]
        documents = [c for d in documents for c in d]
        if randomize:
            random.seed(random_seed)
            random.shuffle(documents)
        if sample_size is not None:
            documents = documents[:sample_size]
        logger.info(f"Loaded {len(documents)} documents")
        return documents
