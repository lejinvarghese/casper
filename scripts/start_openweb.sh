cd  src/app
python3.11 -m venv .venv
source .venv/bin/activate
DATA_DIR=~/.open-webui uvx --python 3.11 open-webui@latest serve
npm start