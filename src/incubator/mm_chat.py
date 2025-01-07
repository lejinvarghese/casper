import click
from llama_index.core.llms import (
    ChatMessage,
    ImageBlock,
    TextBlock,
    MessageRole,
)
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from src.utils.secrets import get_secret

OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

img_path = "./assets/elf.jpg"

msg = ChatMessage(
    role=MessageRole.USER,
    blocks=[
        TextBlock(text="Describe the image?"),
        ImageBlock(path=img_path, image_mimetype="image/jpeg"),
    ],
)

llm = OpenAIMultiModal(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
response = llm.chat(messages=[msg])

click.secho(response, fg="yellow")
