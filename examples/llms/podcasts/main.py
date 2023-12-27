import os
from warnings import filterwarnings
from datetime import datetime
import comet_ml

from pandas import DataFrame
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.metrics import SparseTopKCategoricalAccuracy
from tensorflow.keras.optimizers.schedules import ExponentialDecay
from tensorflow.keras import mixed_precision

from datasets import load_dataset, Dataset
from transformers import (
    AutoTokenizer,
    DefaultDataCollator,
    TFAutoModelForCausalLM,
    AdamWeightDecay,
)

try:
    from src.language.utils.secrets import get_secret
except ModuleNotFoundError:
    from casper.src.language.utils.secrets import get_secret

filterwarnings("ignore")
run_time = datetime.now().strftime("%Y%m%d%H%M%S")
os.environ["COMET_LOG_ASSETS"] = "True"
mixed_precision.set_global_policy("mixed_float16")

COMET_API_KEY = get_secret(secret_id="COMET_API_KEY")

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
    "epochs": 5,
    "batch_size": 16,
    "learning_rate": 1e-4,
    "weight_decay": 0.01,
}

tokenizer = AutoTokenizer.from_pretrained(params["model"])
tokenizer.pad_token = tokenizer.eos_token


def extract_segments(dataset):
    df = DataFrame(dataset).dropna()[["id", "segments"]]
    df = DataFrame(df.set_index("id").segments.explode()).reset_index()
    df["text"] = df["segments"].apply(lambda x: x.get("text"))
    return Dataset.from_pandas(df[["id", "text"]])


def tokenize_function(examples):
    return tokenizer(
        examples["text"], padding="max_length", truncation=True, max_length=256
    )


def create_labels(examples):
    examples["labels"] = examples["input_ids"].copy()
    return examples


def train():
    experiment.log_parameters(params)
    model_checkpoint = params["model"]

    dataset = load_dataset("Whispering-GPT/lex-fridman-podcast", split="train")

    target_topics = [
        "agi",
        # "ai",
        # "learning",
        # "intelligence",
        # "consciousness",
        # "robotics",
        # "psychology",
        # "evolution",
        # "phsyics",
        # "space",
    ]
    filtered_dataset = dataset.filter(
        lambda x: any(s in x["tags"] for s in target_topics)
    ).train_test_split(shuffle=True, seed=42, train_size=50)["train"]
    print(len(dataset))
    print(len(filtered_dataset))
    print(filtered_dataset["title"][:3])

    filtered_dataset = extract_segments(filtered_dataset)

    # tokenize

    data = filtered_dataset.train_test_split(shuffle=True, seed=42, test_size=0.2)
    data_train = data["train"]
    data_val = data["test"]

    data_train_tk = data_train.map(
        tokenize_function,
        batched=True,
        num_proc=16,
        remove_columns=[
            "id",
            "text",
        ],
    )
    data_val_tk = data_val.map(
        tokenize_function,
        batched=True,
        num_proc=8,
        remove_columns=[
            "id",
            "text",
        ],
    )
    data_train_lm = data_train_tk.map(
        create_labels,
        batched=True,
        num_proc=16,
    )
    data_val_lm = data_val_tk.map(
        create_labels,
        batched=True,
        num_proc=8,
    )
    data_collator = DefaultDataCollator(return_tensors="tf")
    train_set = data_train_lm.to_tf_dataset(
        columns=["attention_mask", "input_ids", "labels"],
        shuffle=True,
        batch_size=params["batch_size"],
        collate_fn=data_collator,
    )
    val_set = data_val_lm.to_tf_dataset(
        columns=["attention_mask", "input_ids", "labels"],
        shuffle=True,
        batch_size=params["batch_size"],
        collate_fn=data_collator,
    )

    ## compile model
    model = TFAutoModelForCausalLM.from_pretrained(
        model_checkpoint, pad_token_id=tokenizer.eos_token_id
    )
    lr_schedule = ExponentialDecay(
        initial_learning_rate=params["learning_rate"],
        decay_steps=500,
        decay_rate=0.95,
        staircase=False,
    )

    optimizer = AdamWeightDecay(
        learning_rate=lr_schedule, weight_decay_rate=params["weight_decay"]
    )

    model.compile(
        optimizer=optimizer,
        metrics=[
            SparseTopKCategoricalAccuracy(k=1, name="top_1_accuracy"),
            SparseTopKCategoricalAccuracy(k=5, name="top_5_accuracy"),
        ],
    )

    ## train model
    checkpoint_dir = "./checkpoints"
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")
    checkpoint_callback = ModelCheckpoint(
        filepath=checkpoint_prefix,
        save_weights_only=False,
        save_best_only=False,
        save_freq="epoch",
    )

    early_stopping_callback = EarlyStopping(
        patience=0,
        monitor="val_loss",
    )
    model.fit(
        train_set,
        validation_data=val_set,
        epochs=params["epochs"],
        callbacks=[
            checkpoint_callback,
            early_stopping_callback,
            experiment.get_callback("keras"),
        ],
    )

    model.save("trained_model/final_model")
    experiment.log_model(
        name=f"final_model_{run_time}", file_or_folder="trained_model/final_model"
    )
    experiment.end()
    return model


if __name__ == "__main__":
    train()
