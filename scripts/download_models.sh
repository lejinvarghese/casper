#!/bin/bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# download huggingface model, instructions: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
MODEL_DIR = "${ROOT_DIR}/src/data/.models"
MODEL_NAME=TheBloke/Mistral-7B-Instruct-v0.2-GGUF
QUANT_VERSION=mistral-7b-instruct-v0.2.Q3_K_S.gguf #largest that can fit in a 6GB GPU
huggingface-cli download ${MODEL_NAME} ${QUANT_VERSION} --local-dir ./${MODEL_DIR}/ --local-dir-use-symlinks False