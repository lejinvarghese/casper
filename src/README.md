# Readme

## Get Started

### Step 1: Set up environment

```bash
source src/setup.sh
```

### Step 2: Index Documents

```bash
python3.10 -m src.indexer
```

### Step 3: Compare  LLM Completions with the RAG Completions

```bash
python3.10 -m src.incubator.rag_completion
```

### Step 4: Chat with the model

```bash
python3.10 -m src.chat
```

## Bot

### Step 1: Set up environment
Add environment variables to `.env` file. This requires an environment variable with your Telegram bot token `TELEGRAM_TOKEN`.

```bash
python3.10 -m src.app
```

## Agents

```bash
pip install -r requirements/requirements_agents.txt
```

## Sample Team

```bash
python3.10 -m src.agents.research.team --temperature 0.98
```

## Sample Agent with Tools

```bash
python3.10 -m src.incubator.langgraph.tools_with_persistence --thread_id 20241221190010
```

## Development
    
### Run Tests

```bash
python3.10 -m pytest .
python3.10 -m pytest . -v -n0 ##run sequentially for cursor
```
## Samples

### RAG

```md
Query: "Does emergence in LLMs really happen and when?"
```

![x](../assets/rag.png)

## References
https://www.analyticsvidhya.com/blog/2023/10/rag-pipeline-with-the-llama-index/