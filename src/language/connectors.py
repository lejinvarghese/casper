import os
from typing import List, Union
from arxiv import Client, Search, Result, SortCriterion
from core import Connector
from constants import PDF_DIR
from utils.logger import CustomLogger

logger = CustomLogger(__name__)


class ArxivConnector(Connector):
    """
    A connector to the Arxiv API.
    """

    def __init__(
        self,
        destination_path: str,
        page_size: int = 10,
        delay_seconds: float = 10.0,
        num_retries: int = 20,
    ):
        self._source = "arxiv"
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

    def get_articles_by_ids(
        self, ids=Union[List[str], str], download: bool = True
    ) -> List[Result]:
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

    def get_articles_by_query(
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


if __name__ == "__main__":
    articles = ["2305.18290", "2304.15004", "2312.08782"]
    query = "complexity and emergence in large language models"

    ax = ArxivConnector(destination_path=PDF_DIR)
    results = ax.get_articles_by_ids(articles)
    for r in results:
        logger.info(r.title)
    results = ax.get_articles_by_query(query)
    for r in results:
        logger.info(r.title)
