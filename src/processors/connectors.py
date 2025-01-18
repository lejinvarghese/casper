import os
from typing import List, Union

from arxiv import Client, Result, Search, SortCriterion
from llama_index.core import download_loader
from llama_index.core import Document
from src.core import Connector
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)


class ArxivConnector(Connector):
    """
    A connector to the Arxiv API.
    """

    def __init__(
        self,
        destination_path: str = None,
        page_size: int = 10,
        delay_seconds: float = 10.0,
        num_retries: int = 20,
    ):
        self._source = "arxiv"
        if destination_path:
            os.makedirs(destination_path, exist_ok=True)
        self._destination = destination_path
        self._client = Client(
            page_size=page_size,
            delay_seconds=delay_seconds,
            num_retries=num_retries,
        )

    @property
    def source(self) -> str:
        return self._source

    @property
    def destination(self) -> str:
        return self._destination

    def get_articles_by_ids(self, ids=Union[List[str], str], download: bool = True) -> List[Result]:
        if not isinstance(ids, List):
            ids = [ids]
        search = Search(id_list=ids)
        results = list(self._client.results(search))
        if len(results) == 0:
            logger.warning("No results found")
        else:
            logger.info(f"Found {len(results)} results")
        if download:
            self._download_articles(results)
        return results

    def get_articles_by_topic(
        self,
        query: str,
        max_results: int = 5,
        sort_by: SortCriterion = SortCriterion.SubmittedDate,
        download: bool = True,
    ) -> List[Result]:
        search = Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by,
        )
        results = list(self._client.results(search))
        if len(results) == 0:
            logger.warning("No results found")
        else:
            logger.info(f"Found {len(results)} results")
        if download:
            self._download_articles(results)
        return results

    def _download_articles(self, articles: List[Result]):
        return [a.download_pdf(dirpath=self._destination) for a in articles]


class WebConnector(Connector):
    """
    A connector to text on the web.
    """

    def __init__(self):
        self._source = "web"
        self._destination = "db"
        self.web_reader = download_loader("BeautifulSoupWebReader")()

    @property
    def source(self) -> str:
        return self._source

    @property
    def destination(self) -> str:
        return self._destination

    def get_articles_by_urls(self, urls: Union[List[str], str], custom_hostname: str = None) -> List[Document]:
        if not isinstance(urls, List):
            urls = [urls]
        return self.web_reader.load_data(urls=urls, custom_hostname=custom_hostname)
