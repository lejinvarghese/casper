import os
from src.processors.connectors import ArxivConnector
from src.utils.logger import BaseLogger
from typing import List, Set

logger = BaseLogger(__name__)


class DailyArxivDownloader:
    def __init__(
        self, topic: str, download_dir: str = "src/data/.pdfs", manual_ids_file: str = "src/data/.inputs/arxiv.txt"
    ):
        self.topic = topic
        self.download_dir = download_dir
        self.manual_ids_file = manual_ids_file
        self.connector = ArxivConnector(destination_path=self.download_dir)

    def _read_manual_ids(self) -> Set[str]:
        """Read manually added arxiv IDs from file."""
        if not os.path.exists(self.manual_ids_file):
            return set()

        with open(self.manual_ids_file, "r") as f:
            ids = {line.strip() for line in f if line.strip()[:5]}
        logger.debug(f"Manual IDs read: {ids}")

        # Clear the file after reading
        open(self.manual_ids_file, "w").close()
        return ids

    def _log_downloaded_articles(self, articles: List, source: str):
        """Log information about downloaded articles."""
        for article in articles:
            logger.info(f"Downloaded {source} article: {article.title} (ID: {article.entry_id})")

    def run(self, mode="auto"):
        # Create download directrory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)

        if mode == "auto":
            # Download trending articles
            logger.info(f"Fetching trending articles for topic: {self.topic}")
            trending_articles = self.connector.get_articles_by_topic(query=self.topic, max_results=5, download=True)
            self._log_downloaded_articles(trending_articles, "trending")

        # Process manually added IDs
        elif mode == "manual":
            manual_ids = self._read_manual_ids()
            logger.info(f"Found {len(manual_ids)} manually added article IDs")
            if manual_ids:
                manual_articles = self.connector.get_articles_by_ids(ids=list(manual_ids), download=True)
                self._log_downloaded_articles(manual_articles, "manual")
        else:
            logger.error(f"Mode {mode} not supported. Please use 'auto' or 'manual'.")


if __name__ == "__main__":
    # Configure the topic you're interested in
    topics = ["reinforcement learning", "autonomous vehicles", "complexity science", "information retrieval"]

    for topic in topics:
        dl = DailyArxivDownloader(topic=topic)
        dl.run()

    dl.run(mode="manual")
