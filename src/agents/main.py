import os
import click
from src.utils.secrets import get_secret

os.environ["OPENAI_API_KEY"] = get_secret("OPENAI_API_KEY")
x = get_secret("OPENAI_API_KEY")
click.secho(f"Welcome to the crew!{x}", fg=(52, 225, 235))
