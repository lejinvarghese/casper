from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from llama_index.prompts import PromptTemplate
from constants import INSTRUCTION_MODEL
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
        prompt = PromptTemplate(template=prompt, context_str=kwargs.get("context_str"))
        return self.model.predict(prompt)

    def test(self, context):
        prompt = """<s> [INST] Context: {context_str}. Given this context, generate a highly concise title that summarizes \
        the unique themes found in the context, in no more than 20 words. \
        Dont include descriptions of what you are doing, such as this document summarizes. Be as concise as possible. </s>\

        Title: [/INST]"""
        response = self.generate(prompt, context_str=context)

        logger.info(f"Response: {response}")
