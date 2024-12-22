import pytest
from typing import List

from models import InstructModel, EmbeddingModel
from utils.logger import BaseLogger

logger = BaseLogger(__name__)

EMBEDDING_SIZE = 384
BOS, EOS = "<s>", "</s>"
B_INST, E_INST = "[INST]", "[/INST]"


@pytest.fixture
def sample_query():
    return "Who is Fleetwood Mac?"


@pytest.fixture
def sample_llm():
    return InstructModel()


def test_embedding(sample_query):
    emb = EmbeddingModel(device="cpu")
    response = emb.model.get_text_embedding(sample_query)
    assert response is not None
    assert len(response) == EMBEDDING_SIZE
    assert isinstance(response, List)
    assert isinstance(response[0], float)


@pytest.mark.xdist_group(name="llm")
def test_prompt(sample_llm, sample_query):
    prompt = sample_llm.model.completion_to_prompt(sample_query)
    assert prompt is not None
    assert isinstance(prompt, str)

    tokens = prompt.split(" ")
    assert tokens[0] == BOS
    assert tokens[1] == B_INST
    assert tokens[-1] == E_INST
    logger.info(prompt)


@pytest.mark.xdist_group(name="llm")
def test_response(sample_llm, sample_query):
    response = str(sample_llm.generate(prompt=sample_query))
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    logger.info(response)


@pytest.mark.xdist_group(name="llm")
def test_stream_response(sample_llm, sample_query):
    response = str(sample_llm.generate(prompt=sample_query, streaming=True))
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    logger.info(response)
