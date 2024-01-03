
#!/bin/bash

ROOT_DIR=$(pwd)/src/language
ENVIRONMENT_NAME=".venv"

# step 1: create virtual environment
python3.10 -m venv ${ROOT_DIR}/${ENVIRONMENT_NAME}
source "${ROOT_DIR}/${ENVIRONMENT_NAME}/bin/activate"

# step 2: install default requirements
pip3 install -r ${ROOT_DIR}/requirements_base.txt

# optional: step 2b: if errors that cant find GLIBCXX_3.4.30
SRC_PATH=/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.30
DST_PATH=/home/xx/anaconda3/bin/../lib
rm ${DST_PATH}/libstdc++.so.6
cp ${SRC_PATH} ${DST_PATH}
ln -s ${SRC_PATH} ${DST_PATH}/libstdc++.so.6


# step 3: download huggingface model, instructions: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
MODEL_DIR = "${ROOT_DIR}/data/.models"
MODEL_NAME=TheBloke/Mistral-7B-Instruct-v0.2-GGUF
QUANT_VERSION=mistral-7b-instruct-v0.2.Q3_K_S.gguf #largest that can fit in a 6GB GPU
huggingface-cli download ${MODEL_NAME} ${QUANT_VERSION} --local-dir ./${MODEL_DIR}/ --local-dir-use-symlinks False

# optional: step 4: jupyter  lab kernel
pip3 install -r ${ROOT_DIR}/requirements_lab.txt
python3 -m ipykernel install --user --name=${ENVIRONMENT_NAME} --display-name="${ENVIRONMENT_NAME}"

# step 5: install training requirements
pip3 install -r ${ROOT_DIR}/requirements_train.txt