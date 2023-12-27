import os
import random
from llama_index.readers import PDFReader
from constants import PDF_PATH
from utils.logger import CustomLogger

logger = CustomLogger(__name__)


class PDFLoader:
    """
    A loader for PDF files.
    """

    def __init__(self, source_path: str = PDF_PATH):
        self._source_path = source_path
        self._files = os.listdir(self._source_path)
        self._loader = PDFReader()

    def load_data(self, sample_size: int = None, randomize: bool = False, random_seed: int = 42):
        documents = []
        for i in self._files:
            file_path = os.path.join(self._source_path, i)
            documents.append(self._loader.load_data(file_path))
        documents = [c for d in documents for c in d]
        if randomize:
            random.seed(random_seed)
            random.shuffle(documents)
        if sample_size is not None:
            documents = documents[:sample_size]
        logger.info(f"Loaded {len(documents)} documents")
        return documents
