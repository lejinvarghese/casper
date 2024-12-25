import click
from diffusers import StableDiffusionPipeline
from torch import bfloat16


@click.command()
@click.option(
    "--model_id",
    default="CompVis/stable-diffusion-v1-4",
    help="Model ID to use for generating image",
)
@click.option(
    "--prompt",
    default="fantasy art, astronaut, in space",
    help="Prompt to generate image",
)
@click.option("--device", default="cuda", help="Device to use for generating image")
def generate_image(model_id, prompt, device):
    pipeline = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=bfloat16)
    pipeline.to(device)
    image = pipeline(prompt).images[0]
    file_path = f"src/data/.images/generated_image_{prompt.replace(' ', '_')}.png"
    image.save(file_path)
    return image


if __name__ == "__main__":
    generate_image()
