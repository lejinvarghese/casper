import torch
import click
from llama_cpp import Llama
from src.constants import MISTRAL_MODEL_PATH


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
click.secho(f"Using device: {device}", fg="cyan")


model = Llama(
    model_path=MISTRAL_MODEL_PATH,
    n_ctx=10_000,
    n_threads=8,
    n_gpu_layers=50,
    verbose=False,
)


@click.command()
@click.option("--n_rounds", type=int, default=5)
def main(n_rounds: int):
    base_prompt = "Imagine: A roast battle between comedians Andrew Schulz, Kevin Hart and Whitney Cummings. Be true to each character and their causes. Be short, impactful and crisp."
    output = model(
        f"<s>[INST] {base_prompt} [/INST]",
        max_tokens=256,
        stop=["</s>"],
        echo=True,
    )
    response = output["choices"][0]["text"]
    click.secho(response, fg="yellow")
    click.secho("-" * 100, fg="cyan")
    click.secho(f"Battle for {n_rounds} rounds begins now: ", fg="red")

    for i in range(1, n_rounds):
        prompt = (
            base_prompt
            + f"Responses in the previous round {response} for context. Now based on this, in the next round, get racier, juicier,  take em down, let's go!"
        )
        output = model(
            f"<s>[INST] {prompt} [/INST]",
            max_tokens=1024,
            stop=["</s>"],
            echo=False,
        )
        response = output["choices"][0]["text"]
        click.secho(f"Round {i}:\n{response}", fg="green")
        click.secho("-" * 100, fg="cyan")


if __name__ == "__main__":
    main()
