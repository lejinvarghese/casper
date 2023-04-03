import os
from datetime import datetime
from dotenv import load_dotenv
import comet_ml

from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.metrics import SparseTopKCategoricalAccuracy

from transformers import GPT2Tokenizer
from datasets import load_dataset
from transformers import AutoTokenizer
from transformers import AutoConfig, TFAutoModelForCausalLM
from transformers import AdamWeightDecay
from transformers import DefaultDataCollator
import math

load_dotenv()
run_time = datetime.now().strftime("%Y%m%d%H%M%S")
project_id = "projects-264723"
secret_id = "COMET_API_KEY"


def get_secret(project_id, secret_id, version=1):
    """
    Access a secret- API token, etc- stored in Secret Manager

    Code from https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets#secretmanager-access-secret-version-python
    """
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_id, version)
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    return payload


COMET_API_KEY = get_secret(project_id=project_id, secret_id=secret_id)
os.environ["COMET_LOG_ASSETS"] = "True"

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

params = {
    "model": "distilgpt2",
    "epochs": 2,
    "batch_size": 64,
    "learning_rate": 2e-5,
    "weight_decay": 0.01,
}


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


def train():
    experiment.log_parameters(params)
    model_checkpoint = params["model"]

    dataset = load_dataset("Whispering-GPT/lex-fridman-podcast")

    target_topics = [
        "agi",
        "ai",
        # "intelligence",
        # "learning",
        # "consciousness",
        # "robotics",
        # "psychology",
        # "evolution",
        # "phsyics",
        # "space",
    ]
    filtered_dataset = dataset.filter(
        lambda x: any(s in x["tags"] for s in target_topics)
    )
    print(dataset["train"])
    print(filtered_dataset["train"])
    print(filtered_dataset["train"]["title"][:3])

    ## tokenize
    tokenizer = GPT2Tokenizer.from_pretrained(params["model"])

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

    ## compile model
    config = AutoConfig.from_pretrained(model_checkpoint)
    model = TFAutoModelForCausalLM.from_config(config)
    learning_rate = params["learning_rate"]
    weight_decay = params["weight_decay"]

    optimizer = AdamWeightDecay(
        learning_rate=learning_rate, weight_decay_rate=weight_decay
    )
    # set up checkpointing
    checkpoint_dir = "./checkpoints"
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")
    checkpoint_callback = ModelCheckpoint(
        filepath=checkpoint_prefix,
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

    ##train model

    model.fit(
        train_set,
        epochs=params["epochs"],
        callbacks=[
            checkpoint_callback,
            early_stopping_callback,
            experiment.get_callback("keras"),
        ],
    )

    ##evaluate model
    train_loss = model.evaluate(train_set)
    experiment.log_metrics({"train_loss": train_loss})
    print(f"Perplexity: {math.exp(train_loss):.2f}")
    model.save("trained_model/final_model")
    experiment.log_model(
        name=f"final_model_{run_time}", file_or_folder="trained_model/final_model"
    )
    experiment.end()


if __name__ == "__main__":
    train()
