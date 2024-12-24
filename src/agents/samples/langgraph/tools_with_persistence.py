import os
import json
import click
from datetime import datetime

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage
from langchain_core.messages.ai import AIMessage

from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver


from src.utils.secrets import get_secret
from src.utils.logger import m_colors

os.environ["OPENAI_API_KEY"] = get_secret("OPENAI_API_KEY")

ROOT_DIR = os.getcwd()
STORAGE_PATH = f"{ROOT_DIR}/src/agents/.db/agent_store.db"


class State(TypedDict):
    messages: Annotated[list, add_messages]


class BasicToolNode:
    """A node that runs the tools requested in the last bot message."""

    def __init__(self, tools: list):
        self.tools = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for call in message.tool_calls:
            result = self.tools[call.get("name")].invoke(call.get("args"))
            outputs.append(
                ToolMessage(
                    content=json.dumps(result),
                    name=call.get("name"),
                    tool_call_id=call.get("id"),
                )
            )
        return {"messages": outputs}


def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        message = state[-1]
    elif messages := state.get("messages", []):
        message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(message, "tool_calls") and len(message.tool_calls) > 0:
        return "tools"
    return "__end__"


@click.command()
@click.option("--model_name", default="gpt-4o-mini", help="Model name")
@click.option("--temperature", default=0.7, help="Temperature")
@click.option("--thread_id", default=None, help="Thread ID to continue a conversation")
def main(model_name, temperature, thread_id):
    click.secho("Welcome to the bot garden >>", fg=m_colors.get("yellow"))
    if thread_id is None:

        thread_id = datetime.now().strftime("%Y%m%d%H%M%S")
    click.secho(f"Current thread ID: {thread_id}", fg=m_colors.get("yellow"))

    search = DuckDuckGoSearchResults(max_results=2, verbose=False)
    tools = [search]

    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    llm = llm.bind_tools(tools)

    def chatbot(state):
        return {"messages": [llm.invoke(state.get("messages", []))]}

    tool_nodes = ToolNode(tools=tools)
    memory = SqliteSaver.from_conn_string(STORAGE_PATH)

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.set_entry_point("chatbot")
    graph_builder.add_node("tools", tool_nodes)
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")

    with memory as context:
        app = graph_builder.compile(checkpointer=context)

        while True:
            user_input = click.prompt(click.style("User", fg=m_colors.get("pink")))
            if user_input.lower() in ["quit", "exit", "q"]:
                click.secho(
                    "Assistant: You're now leaving the bot garden, have a nice day, soldier!",
                    fg=m_colors.get("yellow"),
                )
                break
            events = app.stream(
                {"messages": ("user", user_input)},
                config={"configurable": {"thread_id": thread_id}},
            )
            for event in events:
                for value in event.values():
                    message = value.get("messages")[-1]
                    text = message.content
                    if isinstance(message, AIMessage) and text != "":
                        click.secho(f"Assistant: {text}", fg=m_colors.get("aqua"))


if __name__ == "__main__":
    main()
