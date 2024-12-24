PDF_DIR = "src/data/.pdfs"
MODEL_DIR = "src/data/.models"
PERSIST_DIR = "src/data/.storage"

COLLECTION_NAME = "research"

QUANT_VERSION = "mistral-7b-instruct-v0.2.Q3_K_S.gguf"
INSTRUCTION_MODEL_NAME = f"./{MODEL_DIR}/{QUANT_VERSION}"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en"
AGENT_MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"

SUMMARIZATION_PROMPT = """[INST] Context: {context_str}. Given this context, generate a highly concise title that summarizes \
        the unique themes found in the context, in no more than 20 words. \
        Dont include descriptions of what you are doing, such as this document summarizes. Be as concise as possible. </s>\

        Title: [/INST]
"""
NUM_WORKERS = 15
