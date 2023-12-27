import pytest
from typing import List

from models import InstuctModel, EmbeddingModel
from utils.logger import CustomLogger

logger = CustomLogger(__name__)


@pytest.fixture
def sample_query():
    return "who is fleetwood mac?"


def test_embedding(sample_query):
    emb = EmbeddingModel(device="cpu")
    response = emb.model.get_text_embedding(sample_query)
    assert response is not None
    assert len(response) == 384
    assert isinstance(response, List)
    assert isinstance(response[0], float)


def test_prompt(sample_query):
    llm = InstuctModel()
    response = llm.generate(prompt=sample_query)
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    logger.info(response)
