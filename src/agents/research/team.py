import os
from datetime import datetime
import click
from crewai import Agent, Task, Crew, Process

from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import WebsiteSearchTool
from langchain_openai import ChatOpenAI

from src.utils.secrets import get_secret
from src.utils.logger import m_colors
from src.tools.search import search_engine
from src.constants import RESEARCH_DIR

DEFAULT_MODEL_NAME = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_VERBOSITY = False

os.environ["OPENAI_API_KEY"] = get_secret("OPENAI_API_KEY")
current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
web_search = WebsiteSearchTool()


@CrewBase
class ResearchTeam:
    """Research team"""

    def __init__(
        self,
        model_name=DEFAULT_MODEL_NAME,
        temperature=DEFAULT_TEMPERATURE,
        verbose=DEFAULT_VERBOSITY,
    ):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.verbose = verbose

    @agent
    def researcher(self) -> Agent:
        return self._create_agent("researcher", tools=[search_engine, web_search])

    @agent
    def writer(self) -> Agent:
        return self._create_agent("writer")

    @agent
    def editor(self) -> Agent:
        return self._create_agent("editor")

    @task
    def research(self) -> Task:
        return self._create_task("research")

    @task
    def write(self) -> Task:
        return self._create_task("write")

    @task
    def edit(self) -> Task:
        file_path = f"{RESEARCH_DIR}/research_{current_timestamp}.md"
        return self._create_task("edit", output_file=file_path)

    @crew
    def crew(self) -> Crew:
        """Creates the team"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=self.verbose,
            planning=True,
        )

    @before_kickoff
    def before_kickoff_function(self, inputs):
        click.secho(
            f"Team kicked off to analyze research on: {inputs['topic']} at {current_timestamp}.",
            fg=m_colors.get("aqua"),
        )
        return inputs

    @after_kickoff
    def after_kickoff_function(self, result):
        click.secho(
            "Team has completed their research.",
            fg=m_colors.get("aqua"),
        )
        click.secho("-" * 100, fg=m_colors.get("ghost"))
        click.secho(result, fg=m_colors.get("green"))
        return result

    def _create_agent(self, agent_name, **kwargs):
        return Agent(
            config=self.agents_config.get(agent_name),
            verbose=self.verbose,
            llm=self.llm,
            max_iter=self.agents_config.get(agent_name, {}).get("max_iter", 25),
            max_rpm=self.agents_config.get(agent_name, {}).get("max_rpm", 10),
            allow_delegation=self.agents_config.get(agent_name, {}).get(
                "allow_delegation", True
            ),
            **kwargs,
        )

    def _create_task(self, task_name, **kwargs):
        return Task(config=self.tasks_config[task_name], **kwargs)


@click.command()
@click.option("--model_name", default=DEFAULT_MODEL_NAME, type=str, help="Model name")
@click.option(
    "--temperature", default=DEFAULT_TEMPERATURE, type=float, help="Temperature"
)
@click.option(
    "--verbose", default=DEFAULT_VERBOSITY, type=bool, is_flag=True, help="Verbosity"
)
@click.option("--topic", default="complexity science", type=str, help="Topic")
def main(model_name, temperature, verbose, topic):
    return (
        ResearchTeam(
            model_name=model_name,
            temperature=temperature,
            verbose=verbose,
        )
        .crew()
        .kickoff(inputs={"topic": topic})
    )


if __name__ == "__main__":
    main()
