import pytest
from chat import ChatEngine
from src.utils.logger import BaseLogger
logger = BaseLogger(__name__)

@pytest.fixture
def sample_rag_query():
    return "Where was Lejin born?"


@pytest.fixture
def sample_persona_query():
    return "Who are you?"

@pytest.mark.xdist_group(name="llm")
def test_simple_chat(sample_rag_query):
    engine = ChatEngine()
    response = str(engine.chat(sample_rag_query)).lower()
    logger.info(response)
    assert response is not None
    assert "riga" not in response

@pytest.mark.xdist_group(name="llm")
def test_rag_chat(sample_rag_query):
    engine = ChatEngine(chat_mode="condense_plus_context")
    response = str(engine.chat(sample_rag_query)).lower()
    logger.info(response)
    assert response is not None
    assert "riga" in response

@pytest.mark.xdist_group(name="llm")
def test_persona_chat(sample_persona_query):
    persona = "cassia"
    engine = ChatEngine(persona=persona)
    response = str(engine.chat(sample_persona_query)).lower()
    logger.info(response)
    assert response is not None
    assert persona in response
