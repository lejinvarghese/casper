from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class EmbeddingModelAdapter:
    """
    An embedding model adapter that accepts text and generates embeddings.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en",
        batch_size: int = 10,
        device="cuda",
        parallel_process=False,
    ):
        self._model = HuggingFaceEmbedding(
            model_name=model_name,
            device=device,
            embed_batch_size=batch_size,
            parallel_process=parallel_process,
        )

    @property
    def model(self):
        return self._model
