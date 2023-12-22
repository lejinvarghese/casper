# Casper

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name=casper
```

Set up to run on Colab.

# Sample Conversation

Fine tune a language model to listen to Whisper transcripts of a podcast, and answer questions. 5 epochs of supervised fine tuning on a small data sample.

<p align="center">
    <img src="../../../assets/bot_conversation.png" alt="sample" width="600"/>
</p>