from diffusers import StableDiffusionPipeline
import torch

# Load the pre-trained model
pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16)
pipe.to("cuda")

# Generate image from text query
query = "fantasy art, astronaut, in space"
image = pipe(query).images[0]

# Save or display the image
image.save("generated_image.png")
