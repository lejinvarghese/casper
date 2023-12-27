from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from llama_index.prompts import PromptTemplate
from llama_index.embeddings import HuggingFaceEmbedding
from constants import INSTRUCTION_MODEL, EMBEDDING_MODEL, SUMMARIZATION_PROMPT
from utils.logger import CustomLogger

logger = CustomLogger(__name__)


class InstuctModel:
    """
    An instruct model that accepts instructions and generates completions.
    """

    def __init__(
        self,
        model_path: str = INSTRUCTION_MODEL,
        temperature: float = 0.0,
        max_new_tokens: int = 256,
        context_window: int = 3000,
        generate_kwargs: dict = {},
        model_kwargs: dict = {"n_gpu_layers": 50},
    ):
        self.model = LlamaCPP(
            model_path=model_path,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            context_window=context_window,
            generate_kwargs=generate_kwargs,
            model_kwargs=model_kwargs,
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt,
            verbose=False,
        )

    def generate(self, prompt: str, **kwargs) -> str:
        prompt = PromptTemplate(
            template=prompt, context_str=kwargs.get("context_str", "")
        )
        return self.model.predict(prompt)

    def test(self, context: str, prompt: str = SUMMARIZATION_PROMPT):
        response = self.generate(prompt, context_str=context)

        logger.info(f"Response: {response}")


class EmbeddingModel:
    """
    An embedding model that accepts text and generates embeddings.
    """

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        device="cuda",
    ):
        self.model = HuggingFaceEmbedding(model_name=model_name, device=device)

    def test(self):
        text = """fleetwood mac"""
        response = self.model.get_text_embedding(text)
        logger.info(f"Response: {response}")
