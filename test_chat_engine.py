import pytest
from chat import ChatEngine
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)


@pytest.fixture(scope="session")
def chat_engine():
    return ChatEngine()


@pytest.fixture
def dynamic_chat_engine(chat_engine, request):
    """Dynamically configure the ChatEngine based on the test's needs."""
    chat_mode = request.param.get("chat_mode")
    persona = request.param.get("persona")
    chat_engine.update_config(chat_mode=chat_mode, persona=persona)
    return chat_engine


@pytest.fixture
def sample_rag_query():
    return "Where was Lejin born?"


@pytest.fixture
def sample_persona_query():
    return "Who are you?"


@pytest.mark.xdist_group(name="llm")
@pytest.mark.parametrize(
    "dynamic_chat_engine",
    [
        {"chat_mode": "simple", "persona": "casper"},
        {"chat_mode": "condense_plus_context"},
        {"chat_mode": "simple", "persona": "cassia"},
    ],
    indirect=True,
)
def test_chat(dynamic_chat_engine, sample_rag_query, sample_persona_query):
    query = (
        sample_rag_query
        if dynamic_chat_engine.chat_mode == "condense_plus_context"
        else sample_persona_query
    )
    response = str(dynamic_chat_engine.chat(query)).lower()
    logger.info(response)

    # Assert based on configuration
    if dynamic_chat_engine.chat_mode == "condense_plus_context":
        assert "riga" in response
    elif dynamic_chat_engine.persona == "cassia":
        assert "cassia" in response
    if dynamic_chat_engine.chat_mode == "simple":
        assert "riga" not in response