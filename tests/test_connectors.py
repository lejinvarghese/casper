import pytest
from typing import List
from arxiv import Result
from llama_index.schema import Document

from connectors import ArxivConnector, WebConnector
from utils.logger import BaseLogger

logger = BaseLogger(__name__)


@pytest.fixture
def sample_web_url():
    return "https://www.nature.com/articles/d41586-023-04094-z"


@pytest.fixture
def sample_web_substack_url():
    return "https://www.jonstokes.com/p/to-de-risk-ai-the-government-must"


@pytest.fixture
def sample_arxiv_article_id():
    return "2305.18290"


@pytest.fixture
def sample_arxiv_topic():
    return "emergence in large language models"


def test_arxiv_article_id(sample_arxiv_article_id):
    ax = ArxivConnector()
    response = ax.get_articles_by_ids(sample_arxiv_article_id, download=False)
    assert response is not None
    assert isinstance(response, List)
    assert len(response) > 0
    assert isinstance(response[0], Result)
    assert isinstance(response[0].title, str)
    logger.info(response[0].title)


def test_arxiv_topic(sample_arxiv_topic):
    ax = ArxivConnector()
    response = ax.get_articles_by_topic(sample_arxiv_topic, download=False)
    assert response is not None
    assert isinstance(response, List)
    assert len(response) > 1
    assert isinstance(response[0], Result)
    assert isinstance(response[0].title, str)
    logger.info(response[0].title)


def test_web_url(sample_web_url):
    wc = WebConnector()
    response = wc.get_articles_by_urls(sample_web_url)
    assert response is not None
    assert isinstance(response, List)
    assert len(response) > 0
    assert isinstance(response[0], Document)
    logger.info(response[0])


def test_web_substack_url(sample_web_substack_url):
    wc = WebConnector()
    response = wc.get_articles_by_urls(sample_web_substack_url)
    assert response is not None
    assert isinstance(response, List)
    assert len(response) > 0
    assert isinstance(response[0], Document)
    logger.info(response[0])
