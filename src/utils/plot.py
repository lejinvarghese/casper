from PIL import Image
from io import BytesIO


def draw_langgraph(graph, dpi=300, suffix="sample.png"):
    """Draws the language graph and saves it as a PNG image."""
    img = graph.get_graph().draw_mermaid_png()
    img = Image.open(BytesIO(img))
    img.save(f"assets/lg_{suffix}", dpi=(dpi, dpi))
