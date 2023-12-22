
## Get Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
python -m ipykernel install --user --name=.venv --display-name="mistral"
```