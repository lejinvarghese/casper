## Setup

### Dependencies

```bash

## step 1: create a virtual environment
uv init
uv venv --python 3.11
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
python3.11 -m src.indexer
```

## Features

### A: Chat with the model

```bash
python3.11 -m src.chat
```

### B: Chat with a telegram app

```bash
python3.11 -m src.app
```

### C: Deploy a research team

```bash
python3.11 -m src.agents.research.team --temperature 0.0
```

### D: Chat with a model with memory

```bash
python3.11 -m src.incubator.langgraph.tools_with_persistence --thread_id 20241221190010
```

### E: Compare  LLM Completions with the RAG Completions

```bash
python3.11 -m src.incubator.rag_completion
```

### F: Generate an image

```bash
python3.11 -m src.tools.image --n_results 1
```

### G: Run  a simulation

```bash
python3.11 -m src.simulation.main
```

## Development

#### Run server
```bash
MODEL_NAME=mistral-7b-instruct-v0.2.Q3_K_S.gguf
MODEL_NAME=Qwen2-VL-2B-Instruct-Q8_0.gguf
MODEL_NAME=llava-llama-3-8b-v1_1-int4.gguf
llama-server -m ./models/$MODEL_NAME --port 8888 --n-gpu-layers 99
```

```bash
MODEL_DIR=/media/starscream/wheeljack1/projects/casper/.venv/llama.cpp/models
cd $MODEL_DIR
REPO_ID=bartowski/deepthought-8b-llama-v0.01-alpha-GGUF
FILE_NAME=deepthought-8b-llama-v0.01-alpha-IQ3_XS.gguf

huggingface-cli download $REPO_ID  $FILE_NAME --local-dir-use-symlinks False --local-dir .
```
    
### Run Tests

```bash
python3.11 -m pytest .
```