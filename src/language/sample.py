import torch
from llama_cpp import Llama
from src.language.constants import MODEL_DIR, QUANT_VERSION

MODEL_PATH = f"./{MODEL_DIR}/{QUANT_VERSION}"

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


model = Llama(
    model_path=MODEL_PATH,
    n_ctx=10_000,
    n_threads=8,
    n_gpu_layers=50,
)


def main():
    base_prompt = "Imagine: A roast battle between comedians Andrew Schulz, Kevin Hart and Whitney Cummings. Be true to each character and their causes. Be short, impactful and crisp."
    output = model(
        f"<s>[INST] {base_prompt} [/INST]",
        max_tokens=256,
        stop=["</s>"],
        echo=True,
    )
    response = output["choices"][0]["text"]
    print(response)

    for i in range(1, 5):
        prompt = (
            base_prompt
            + f"Responses in the previous round {response} for context. Now based on this, in the next round, get racier, juicier,  take em down, let's go!"
        )
        output = model(
            f"<s>[INST] {prompt} [/INST]",
            max_tokens=256,
            stop=["</s>"],
            echo=False,
        )
        response = output["choices"][0]["text"]
        print(f"Round {i}: {response}")


if __name__ == "__main__":
    main()
