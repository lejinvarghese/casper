import torch
from ctransformers import (
    AutoModelForCausalLM,
)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

MODEL_NAME = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
QUANT_TYPE = "mistral-7b-instruct-v0.2.Q3_K_S.gguf"
MODEL_TYPE = "mistral"
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    model_file=QUANT_TYPE,
    model_type=MODEL_TYPE,
    gpu_layers=50,
)


def main():
    prompt = "What is effective acceleration is going to help in the world?"
    response = model(
        prompt=prompt,
        stream=True,
        temperature=0.9,
    )
    for text in response:
        print(text, end="", flush=True)


if __name__ == "__main__":
    main()
