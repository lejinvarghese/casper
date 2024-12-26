from langchain_community.tools import DuckDuckGoSearchResults
from click import secho
from crewai.tools import tool


@tool("Search")
def search(question: str) -> str:
    """Search the internet for information"""
    search_engine = DuckDuckGoSearchResults(
        verbose=False,
        response_format="content_and_artifact",
        output_format="list",
        num_results=10,
    )
    try:
        results = search_engine.run(question)
        secho(f"Search successful, returned: {len(results)} results", fg="green")
        return results
    except Exception as e:
        secho(f"Search encountered an error: {e}", fg="red")
        return f"Search encountered an error: {e}"
