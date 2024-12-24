
#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$SCRIPT_DIR"
ENVIRONMENT_NAME=".venv"
VENV_PATH="${ROOT_DIR}/${ENVIRONMENT_NAME}"
VENV_BIN="${VENV_PATH}/bin"

echo "Creating virtual environment in: ${ROOT_DIR}/${ENVIRONMENT_NAME}"
# step 0: remove existing environment if it exists
rm -rf ${VENV_PATH}

# step 1: create virtual environment
python3.10 -m venv ${VENV_PATH}
source "${VENV_BIN}/activate"
echo "Using Python from: $(which python)"
echo "Virtual environment location: $VIRTUAL_ENV"

# step 2: install default requirements
${VENV_BIN}/python -m ensurepip --upgrade
${VENV_BIN}/python -m pip install --upgrade pip
${VENV_BIN}/python -m pip install --upgrade pip
${VENV_BIN}/pip cache purge
${VENV_BIN}/pip install --no-cache-dir -r ${ROOT_DIR}/requirements/requirements.txt

export CMAKE_ARGS="-DLLAMA_CUBLAS=on"
export FORCE_CMAKE=1
${VENV_BIN}/pip install --no-cache-dir -r ${ROOT_DIR}/requirements/requirements_chat.txt
${VENV_BIN}/pip install --no-cache-dir -r ${ROOT_DIR}/requirements/requirements_agents.txt

## install llama-cpp-python with CUDA support
# CMAKE_ARGS="-DGGML_CUDA=on" pip install --no-cache-dir llama-index-llms-llama-cpp==0.3.0

# # optional: step 2b: if errors that cant find GLIBCXX_3.4.30
# SRC_PATH=/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.30
# DST_PATH=/home/xx/anaconda3/bin/../lib
# rm ${DST_PATH}/libstdc++.so.6
# cp ${SRC_PATH} ${DST_PATH}
# ln -s ${SRC_PATH} ${DST_PATH}/libstdc++.so.6


# # step 3: download huggingface model, instructions: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
# MODEL_DIR = "${ROOT_DIR}/data/.models"
# MODEL_NAME=TheBloke/Mistral-7B-Instruct-v0.2-GGUF
# QUANT_VERSION=mistral-7b-instruct-v0.2.Q3_K_S.gguf #largest that can fit in a 6GB GPU
# huggingface-cli download ${MODEL_NAME} ${QUANT_VERSION} --local-dir ./${MODEL_DIR}/ --local-dir-use-symlinks False

# # optional: step 4: jupyter  lab kernel
# pip3 install -r ${ROOT_DIR}/requirements_lab.txt
# python3 -m ipykernel install --user --name=${ENVIRONMENT_NAME} --display-name="${ENVIRONMENT_NAME}"

# # step 5: install training requirements
# pip3 install -r ${ROOT_DIR}/requirements_train.txt