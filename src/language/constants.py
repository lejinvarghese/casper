PDF_DIR = "src/language/data/.pdfs"
MODEL_DIR = "src/language/data/.models"
PERSIST_DIR = "src/language/data/.storage"

COLLECTION_NAME = "research"

QUANT_VERSION = "mistral-7b-instruct-v0.2.Q3_K_S.gguf"
INSTRUCTION_MODEL = f"./{MODEL_DIR}/{QUANT_VERSION}"
EMBEDDING_MODEL = "BAAI/bge-small-en"
AGENT_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

SUMMARIZATION_PROMPT = """<s> [INST] Context: {context_str}. Given this context, generate a highly concise title that summarizes \
        the unique themes found in the context, in no more than 20 words. \
        Dont include descriptions of what you are doing, such as this document summarizes. Be as concise as possible. </s>\

        Title: [/INST]
"""
NUM_WORKERS = 15
