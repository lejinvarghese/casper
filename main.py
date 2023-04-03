import os
from datetime import datetime
from dotenv import load_dotenv
import comet_ml

from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.metrics import SparseTopKCategoricalAccuracy

# from transformers import GPT2Tokenizer

load_dotenv()
run_time = datetime.now().strftime("%Y%m%d%H%M%S")

COMET_API_KEY = os.getenv("COMET_API_KEY")
params = {
    "model": "distilgpt2",
    "epochs": 2,
    "batch_size": 1024,
    "learning_rate": 2e-5,
    "weight_decay": 0.01,
}

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
    tokenizer_checkpoint = params["model"]
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_checkpoint)
    return tokenizer(examples["text"])


def group_texts(examples):
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
    total_length = len(concatenated_examples[list(examples.keys())[0]])
    block_size = 128
    total_length = (total_length // block_size) * block_size

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


def train():
    experiment.log_parameters(params)
    model_checkpoint = params["model"]

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
    # tokenizer = GPT2Tokenizer.from_pretrained(params["model"])

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
    model = TFAutoModelForCausalLM.from_config(config)
    learning_rate = params["learning_rate"]
    weight_decay = params["weight_decay"]

    optimizer = AdamWeightDecay(
        learning_rate=learning_rate, weight_decay_rate=weight_decay
    )
    checkpoint_callback = ModelCheckpoint(
        filepath="trained_model/checkpoints",  # customize checkpoint file name
        save_weights_only=False,
        save_best_only=False,
        save_freq="epoch",
    )
    early_stopping_callback = EarlyStopping(patience=2)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=[
            SparseTopKCategoricalAccuracy(k=1, name="top_1_accuracy"),
            SparseTopKCategoricalAccuracy(k=5, name="top_5_accuracy"),
        ],
    )

    data_collator = DefaultDataCollator(return_tensors="tf")

    train_set = lm_datasets["train"].to_tf_dataset(
        columns=["attention_mask", "input_ids", "labels"],
        shuffle=True,
        batch_size=params["batch_size"],
        collate_fn=data_collator,
    )

    model.fit(
        train_set,
        epochs=params["epochs"],
        callbacks=[checkpoint_callback, early_stopping_callback],
    )
    experiment.get_callback("keras")
    train_loss = model.evaluate(train_set)
    experiment.log_metrics({"train_loss": train_loss})
    print(f"Perplexity: {math.exp(train_loss):.2f}")
    model.save("trained_model")
    experiment.log_model(
        name=f"saved_model_{run_time}", file_or_folder="trained_model/"
    )
    experiment.end()


if __name__ == "__main__":
    train()
