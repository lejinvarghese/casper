import re
from llama_cpp import Llama
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.llms.llama_cpp.llama_utils import (
    completion_to_prompt,
    messages_to_prompt,
)
from concordia.language_model.language_model import LanguageModel, InvalidResponseError
from src.constants import MISTRAL_MODEL_PATH
from src.utils.logger import BaseLogger


logger = BaseLogger(__name__)


class MistralModelAdapter:
    """
    A model adapter for Mistral.
    """

    def __init__(
        self,
        model_path: str = MISTRAL_MODEL_PATH,
        temperature: float = 0.0,
        max_new_tokens: int = 1024,
        context_window: int = 3000,
        generate_kwargs: dict = {},
        model_kwargs: dict = {"n_gpu_layers": 60},
        system_prompt: str = "",
    ):
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

    @property
    def model(self):
        return self._model

    def generate(self, prompt: str, streaming: bool = False, **kwargs) -> str:
        if streaming:
            return self.model.stream_complete(
                prompt, context_str=kwargs.get("context_str", "")
            )
        else:
            return str(
                self.model.complete(prompt, context_str=kwargs.get("context_str", ""))
            )


class LLamaModelAdapter:
    def __init__(
        self,
        repo_id: str = "MaziyarPanahi/SmolLM-1.7B-Instruct-GGUF",
        filename: str = "SmolLM-1.7B-Instruct.Q2_K.gguf",
        n_gpu_layers: int = 60,
        chat_format: str = "chatml",
        verbose: bool = False,
        **kwargs,
    ):
        self._model = Llama.from_pretrained(
            repo_id=repo_id,
            filename=filename,
            n_gpu_layers=n_gpu_layers,
            chat_format=chat_format,
            verbose=verbose,
            n_ctx=8192,
            **kwargs,
        )

    @property
    def model(self):
        return self._model

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 2048,
        stop: list[str] = ["<|im_end|>"],
        streaming: bool = False,
        **kwargs,
    ) -> str:
        response = self.model.create_chat_completion(
            messages=messages,
            stream=streaming,
            temperature=temperature,
            stop=stop,
            max_tokens=max_tokens,
            **kwargs,
        )
        if streaming:
            return response
        else:
            return response.get("choices", [])[0].get("message", {}).get("content")


class SimulationModelAdapter(LanguageModel):
    """A model adapter for concordia model simulations."""

    def __init__(self, **kwargs) -> None:
        self._model = LLamaModelAdapter(**kwargs)

    @property
    def model(self):
        return self._model

    def sample_text(
        self,
        prompt: str,
        max_tokens: int = 1024,
        max_characters: int = 10,
        temperature: float = 0.1,
        **kwargs,
    ) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.model.generate(
            messages=messages, temperature=temperature, max_tokens=max_tokens
        )
        return response

    def sample_choice(
        self, prompt: str, responses: list[str], max_attempts: int = 10
    ) -> tuple[int, str, dict[str, float]]:
        max_characters = len(max(responses, key=len))

        attempts = 1
        prompt = (
            prompt
            + "\nRespond EXACTLY with one of the following options:\n"
            + "\n".join(responses)
            + "."
        )

        for _ in range(max_attempts):
            temperature = 0.0
            if attempts > 1:
                temperature = 0.5

            sample = self.sample_text(
                prompt,
                max_characters=max_characters,
                temperature=temperature,
            )
            answer = self.__extract_choice_response(sample)
            try:
                idx = responses.index(answer)
            except ValueError:
                attempts += 1
                continue
            else:
                debug = {}
                return idx, responses[idx], debug

        raise InvalidResponseError("Too many multiple choice attempts.")

    def __extract_choice_response(self, sample: str) -> str | None:
        if len(sample) == 1:
            return sample
        elif len(sample) == 2:
            return sample[0]
        else:
            return self.__extract_parenthesized_choice(sample)

    def __extract_parenthesized_choice(self, sample: str):
        match = re.search(r"\(?(\w)\)", sample)
        if match:
            return match.group(1)
        else:
            return None
