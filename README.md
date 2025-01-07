# Casper

<p align="center">
    <img src="./assets/casper.png" alt="casper" width="600"/>
</p>

Casper, the destiny of beautiful souls.


## Setup

### Dependencies

```bash

## step 1: create a virtual environment
uv init
source .venv/bin/activate

## step 2: lock dependencies [migrate to uv.lock when necessary]
uv pip compile pyproject.toml -o requirements.txt

## step 3: install dependencies
uv pip install -r requirements.txt

## step 4: add new dependencies
uv add <package-name>

### rerun step 2 after adding new dependencies
```

### Environment Variables

Add environment variables to `.env` file.

```bash
TELEGRAM_TOKEN=<your-telegram-token>
OPENAI_API_KEY=<your-openai-api-key>
```

### Optional: Download local models

```bash
sh scripts/download_models.sh
```


### Optional: Index Documents

```bash
python3.10 -m src.indexer
```

## Features

### A: Chat with the model

```bash
python3.10 -m src.chat
```

### B: Chat with a telegram app

```bash
python3.10 -m src.app
```

### C: Deploy a research team

```bash
python3.10 -m src.agents.research.team --temperature 0.0
```

### D: Chat with a model with memory

```bash
python3.10 -m src.incubator.langgraph.tools_with_persistence --thread_id 20241221190010
```

### E: Compare  LLM Completions with the RAG Completions

```bash
python3.10 -m src.incubator.rag_completion
```

### F: Generate an image

```bash
python3.10 -m src.tools.image --n_results 1
```

### G: Run  a simulation

```bash
python3.10 -m src.simulation.main
```

## Development

```Run server
MODEL_NAME=mistral-7b-instruct-v0.2.Q3_K_S.gguf
MODEL_NAME=Qwen2-VL-2B-Instruct-Q8_0.gguf
llama-server -m ./models/$MODEL_NAME --port 8888 --n-gpu-layers 99
```
    
### Run Tests

```bash
python3.10 -m pytest .
python3.10 -m pytest . -v -n0 ##run sequentially for cursor
```
### Examples

#### RAG

```md
Query: "Does emergence in LLMs really happen and when?"
```

![rag](assets/rag.png)

#### Casper Art

- first image
![x](https://im.runware.ai/image/ii/00a4384e-275c-4eae-8e4c-c4e4d363f9c6.JPG)