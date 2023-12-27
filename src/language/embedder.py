from llama_index.embeddings import HuggingFaceEmbedding
from constants import EMBEDDING_MODEL
from utils.logger import CustomLogger

logger = CustomLogger(__name__)


class EmbeddingModel:
    """
    An embedding model that accepts text and generates embeddings.
    """

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
    ):
        self.model = HuggingFaceEmbedding(model_name=model_name)

    def get_embeddings(self, text: str) -> str:
        return self.model.get_text_embedding(text)

    def test(self):
        text = """fleetwood mac"""
        response = self.get_embeddings(text)
        logger.info(f"Response: {response}")
