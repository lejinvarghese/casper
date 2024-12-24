# Casper

<p align="center">
    <img src="./assets/casper.png" alt="casper" width="600"/>
</p>

Casper, the destiny of beautiful souls.


## Setup

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
