import os
from dotenv import load_dotenv
import comet_ml
from transformers import GPT2Tokenizer


load_dotenv()

COMET_API_KEY = os.getenv("COMET_API_KEY")
experiment = comet_ml.Experiment(
    api_key=COMET_API_KEY,
    project_name="clm",
    log_code=True,
    auto_metric_logging=True,
    auto_param_logging=True,
    auto_histogram_weight_logging=True,
    auto_histogram_gradient_logging=True,
    auto_histogram_activation_logging=True,
)


def tokenize_function(examples):
    from transformers import GPT2Tokenizer

    tokenizer = GPT2Tokenizer.from_pretrained(params["model"])
    return tokenizer(examples["text"])


def group_texts(examples):
    # Concatenate all texts.
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
    total_length = len(concatenated_examples[list(examples.keys())[0]])
    # We drop the small remainder, we could add padding if the model supported it instead of this drop, you can
    # customize this part to your needs.
    # block_size = tokenizer.model_max_length
    block_size = 128
    total_length = (total_length // block_size) * block_size
    # Split by chunks of max_len.
    result = {
        k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
        for k, t in concatenated_examples.items()
    }
    result["labels"] = result["input_ids"].copy()
    return result


from datasets import load_dataset
from transformers import AutoTokenizer
from transformers import AutoConfig, TFAutoModelForCausalLM
from transformers import AdamWeightDecay
from transformers import DefaultDataCollator
import math
import pandas as pd


if __name__ == "__main__":
    params = {
        "model": "distilgpt2",
        "epochs": 50,
        "batch_size": 32,
        "learning_rate": 2e-5,
        "weight_decay": 0.01,
    }
    experiment.log_parameters(params)
    model_checkpoint = params["model"]
    tokenizer_checkpoint = params["model"]

    dataset = load_dataset("Whispering-GPT/lex-fridman-podcast")

    target_topics = [
        "agi",
        "ai",
        "intelligence",
        "learning",
        "consciousness",
        "robotics",
        "psychology",
        "evolution",
        "phsyics",
        "space",
    ]
    filtered_dataset = dataset.filter(
        lambda x: any(s in x["tags"] for s in target_topics)
    )
    print(dataset["train"])
    print(filtered_dataset["train"])
    print(filtered_dataset["train"]["title"][:3])

    ## tokenize
    tokenizer = GPT2Tokenizer.from_pretrained(params["model"])
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_checkpoint)
    tokenized_datasets = filtered_dataset.map(
        tokenize_function,
        batched=True,
        num_proc=4,
        remove_columns=[
            "id",
            "channel",
            "channel_id",
            "title",
            "categories",
            "tags",
            "description",
            "text",
            "segments",
        ],
    )
    lm_datasets = tokenized_datasets.map(
        group_texts,
        batched=True,
        batch_size=1000,
        num_proc=4,
    )

    ## train
    config = AutoConfig.from_pretrained(model_checkpoint)
    gpt2 = TFAutoModelForCausalLM.from_config(config)
    learning_rate = params["learning_rate"]
    weight_decay = params["weight_decay"]

    optimizer = AdamWeightDecay(
        learning_rate=learning_rate, weight_decay_rate=weight_decay
    )
    gpt2.compile(optimizer=optimizer)

    data_collator = DefaultDataCollator(return_tensors="tf")

    train_set = lm_datasets["train"].to_tf_dataset(
        columns=["attention_mask", "input_ids", "labels"],
        shuffle=True,
        batch_size=params["batch_size"],
        collate_fn=data_collator,
    )

    # gpt2.fit(train_set, epochs=params["epochs"])
    # eval_loss = gpt2.evaluate(train_set)
    # experiment.log_metrics({"eval_loss": eval_loss})
    # print(f"Perplexity: {math.exp(eval_loss):.2f}")
