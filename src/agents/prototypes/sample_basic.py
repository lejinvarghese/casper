import os
import click

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from src.utils.secrets import get_secret
from src.utils.logger import m_colors

os.environ["OPENAI_API_KEY"] = get_secret("OPENAI_API_KEY")


@click.command()
@click.option("--model_name", default="gpt-4o-mini", help="Model name")
@click.option("--temperature", default=0.7, help="Temperature")
def main(model_name, temperature):
    click.secho("Welcome to the bot garden >>", fg=m_colors.get("yellow"))
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    def chatbot(state):
        return {"messages": [llm.invoke(state["messages"])]}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")
    graph = graph_builder.compile()
    while True:
        user_input = click.prompt(click.style("User", fg=m_colors.get("aqua")))
        if user_input.lower() in ["quit", "exit", "q"]:
            click.secho(
                ">> You're now leaving the bot garden, toodaloo!",
                fg=m_colors.get("yellow"),
            )
            break
        for event in graph.stream({"messages": ("user", user_input)}):
            for value in event.values():
                text = value.get("messages")[-1].content
                click.secho(f"Assistant: {text}", fg=m_colors.get("pink"))


if __name__ == "__main__":
    main()
