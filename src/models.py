from collections.abc import Sequence
from concordia.language_model.language_model import LanguageModel
from typing_extensions import override

import random

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.llms.llama_cpp.llama_utils import (
    completion_to_prompt,
    messages_to_prompt,
)
from src.constants import EMBEDDING_MODEL_NAME, INSTRUCTION_MODEL_NAME
from src.utils.logger import BaseLogger


_MAX_MULTIPLE_CHOICE_ATTEMPTS = 3
_DEFAULT_TEMPERATURE = 0.5
_DEFAULT_MAX_TOKENS = 1024

logger = BaseLogger(__name__)


class InstructModel:
    """
    An instruct model that accepts instructions and generates completions.
    """

    def __init__(
        self,
        model_path: str = INSTRUCTION_MODEL_NAME,
        temperature: float = 0.0,
        max_new_tokens: int = 1024,
        context_window: int = 3000,
        generate_kwargs: dict = {},
        model_kwargs: dict = {"n_gpu_layers": 60},
        system_prompt: str = "",
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
            system_prompt=system_prompt,
        )

    def generate(self, prompt: str, streaming: bool = False, **kwargs) -> str:
        if streaming:
            return self.model.stream_complete(
                prompt, context_str=kwargs.get("context_str", "")
            )
        else:
            return self.model.complete(
                prompt, context_str=kwargs.get("context_str", "")
            )


class EmbeddingModel:
    """
    An embedding model that accepts text and generates embeddings.
    """

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL_NAME,
        batch_size: int = 10,
        device="cuda",
    ):
        self.model = HuggingFaceEmbedding(
            model_name=model_name, device=device, embed_batch_size=batch_size
        )


class SimulationModel(LanguageModel):
    """Model adapter."""

    def __init__(
        self,
        model_path: str = INSTRUCTION_MODEL_NAME,
        temperature: float = _DEFAULT_TEMPERATURE,
        max_new_tokens: int = _DEFAULT_MAX_TOKENS,
        context_window: int = 3000,
        generate_kwargs: dict = {},
        model_kwargs: dict = {"n_gpu_layers": 60},
        system_prompt: str = "",
    ) -> None:
        self._model = LlamaCPP(
            model_path=model_path,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            context_window=context_window,
            generate_kwargs=generate_kwargs,
            model_kwargs=model_kwargs,
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt,
            verbose=False,
            system_prompt=system_prompt,
        )
        self._system_message = system_prompt

    @override
    def sample_text(
        self,
        prompt: str,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        temperature: float = _DEFAULT_TEMPERATURE,
    ) -> str:

        self._model.temperature = temperature
        self._model.max_new_tokens = max_tokens
        response = self._model.complete(prompt)
        return response

    @override
    def sample_choice(
        self,
        prompt: str,
        responses: Sequence[str],
    ) -> tuple[int, str, dict[str, float]]:

        samples = []

        for a in range(_MAX_MULTIPLE_CHOICE_ATTEMPTS):
            temperature = self.dynamically_adjust_temperature(
                a, _MAX_MULTIPLE_CHOICE_ATTEMPTS
            )

            sample = self.sample_text(
                prompt,
                temperature=temperature,
            )
            samples.append(str(sample))
        debug = {}
        answer = random.choice(samples)
        idx = samples.index(answer)
        return idx, answer, debug

    def dynamically_adjust_temperature(
        self,
        attempts: int,
        max_attempts: int,
    ) -> float:
        """Adjusts choice sampling temperature based on number of attempts so far."""
        temperature = 0.0
        if attempts > 1 and attempts < (max_attempts / 2.0):
            temperature = 0.5
        elif attempts > (max_attempts / 2.0):
            temperature = 0.75
        return temperature
