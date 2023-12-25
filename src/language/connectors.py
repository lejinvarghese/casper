# from core import Connector

# class Arxiv(Connector):
#     pass

from llama_index import download_loader

ArxivReader = download_loader("ArxivReader")

topic  = "emergence of complex intelligence in neural networks".replace(" ", "+")
query = f"-announced_date_first; size: 5; include_cross_list: True; terms: AND abstract={topic}"
loader = ArxivReader()
documents= loader.load_data(search_query="complex intelligence")
print(len(documents))
print(documents)