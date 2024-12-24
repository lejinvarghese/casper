# Casper

<p align="center">
    <img src="./assets/casper.png" alt="casper" width="600"/>
</p>

Casper, the destiny of beautiful souls.


## Setup

```bash
uv init
source .venv/bin/activate

#lock dependencies
uv pip compile pyproject.toml -o requirements.txt

#install dependencies
uv pip install -r requirements.txt

# add new dependencies
uv add <package-name>


```
