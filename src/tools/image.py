import click
import re
import asyncio
from runware import Runware, IImageInference, IPromptEnhance
from runware.types import ILora
from src.utils.secrets import get_secret

RUNWARE_API_KEY = get_secret("RUNWARE_API_KEY")

DEFAULT_MODEL_ID = "runware:101@1"
DEFAULT_DIMENSION = "768x1152"
N_RESULTS = 1
DEFAULT_PROMPT = """
A stunning female wizard stands poised in a magical dark fantasy realm, casting a mesmerizing spell with elemental energies swirling around her. She wears an alluring off-shoulder costume adorned with elaborate rings, showcasing intricate details and textures. Her beautiful, fair skin glows under soft, ethereal lighting, emphasizing her enchanting blue eyes and captivating smile. Elements of fire, water, wind, and ice dance in a perfect dynamic composition surrounding her, creating a breathtaking, ultra realistic, high-resolution masterpiece, hdr -(mutilated fingers, fingers, sadness, disfigured face)
"""


def extract_prompt_elements(text):
    match = re.match(r"^(.*?)\((.*?)\)$", text.strip())
    if match:
        positive, negative = match.groups()
        return positive.strip()[:-1], negative.strip()
    return text.strip(), None


async def generate_image(
    model_id=DEFAULT_MODEL_ID,
    prompt=DEFAULT_PROMPT,
    n_results=N_RESULTS,
    dimension=DEFAULT_DIMENSION,
    enhance=False,
    add_lora=False,
) -> list[str]:
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()

    pos_prompt, neg_prompt = extract_prompt_elements(prompt)
    width, height = map(int, dimension.split("x"))
    click.secho(f"Positive Prompt: {pos_prompt}", fg="green")
    click.secho(f"Negative Prompt: {neg_prompt}", fg="red")

    if enhance:
        prompt_enhancer = IPromptEnhance(
            prompt=pos_prompt[:300],
            promptVersions=1,
            promptMaxLength=300,
        )
        pos_prompt = await runware.promptEnhance(promptEnhancer=prompt_enhancer)
        pos_prompt = pos_prompt[0].text
        click.secho(f"Enhanced Prompt: {pos_prompt}", fg="green")

    if add_lora:
        lora = [
            ILora(model="civitai:340248@755549", weight=0.2),
            ILora(model="civitai:308147@880134", weight=0.2),
        ]
    else:
        lora = None
    request_image = IImageInference(
        positivePrompt=pos_prompt,
        model=model_id,
        numberResults=n_results,
        negativePrompt=neg_prompt,
        height=height,
        width=width,
        lora=lora,
    )

    images = await runware.imageInference(requestImage=request_image)
    return images


@click.command()
@click.option(
    "--model_id",
    default=DEFAULT_MODEL_ID,
    help="Model ID to use for generating image",
)
@click.option(
    "--prompt",
    default=DEFAULT_PROMPT,
    help="Prompt to generate image",
)
@click.option("--n_results", default=N_RESULTS, help="number of results to generate")
@click.option("--dimension", default=DEFAULT_DIMENSION, help="Image dimension")
@click.option("--enhance", default=False, is_flag=True, help="Enhance prompt")
@click.option("--add_lora", default=True, is_flag=True, help="Add Lora adapters")
def main(model_id, prompt, n_results, dimension, enhance, add_lora):
    images = asyncio.run(generate_image(model_id, prompt, n_results, dimension, enhance, add_lora=add_lora))
    for image in images:
        click.secho(f"Image URL: {image.imageURL}", fg="blue")
    return images


if __name__ == "__main__":
    main()
