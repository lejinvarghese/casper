import os
from datetime import datetime
import click
from crewai import Agent, Task, Crew, Process

from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from langchain_openai import ChatOpenAI

from src.utils.secrets import get_secret
from src.utils.logger import m_colors
from src.utils.tools import search

os.environ["OPENAI_API_KEY"] = get_secret("OPENAI_API_KEY")
now = datetime.now().strftime("%Y%m%d%H%M%S")


@CrewBase
class ResearchTeam:
    """Research team"""

    def __init__(self, model_name, temperature, verbose):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.verbose = verbose
        self.tools = [search]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config.get("researcher"),
            verbose=self.verbose,
            llm=self.llm,
            tools=self.tools,
            max_iter=self.agents_config.get("researcher", {}).get("max_iter", 25),
            max_rpm=self.agents_config.get("researcher", {}).get("max_rpm", 10),
            allow_delegation=self.agents_config.get("researcher", {}).get(
                "allow_delegation", True
            ),
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config.get("writer"),
            verbose=self.verbose,
            llm=self.llm,
            max_iter=self.agents_config.get("writer", {}).get("max_iter", 25),
            max_rpm=self.agents_config.get("writer", {}).get("max_rpm", 10),
            allow_delegation=self.agents_config.get("writer", {}).get(
                "allow_delegation", True
            ),
        )

    @agent
    def editor(self) -> Agent:
        return Agent(
            config=self.agents_config.get("editor"),
            verbose=self.verbose,
            llm=self.llm,
            max_iter=self.agents_config.get("editor", {}).get("max_iter", 25),
            max_rpm=self.agents_config.get("editor", {}).get("max_rpm", 10),
            allow_delegation=self.agents_config.get("editor", {}).get(
                "allow_delegation", False
            ),
        )

    @task
    def research(self) -> Task:
        return Task(
            config=self.tasks_config["research"],
            agent=self.researcher(),
        )

    @task
    def write(self) -> Task:
        return Task(
            config=self.tasks_config["write"],
            agent=self.writer(),
        )

    @task
    def edit(self) -> Task:
        return Task(
            config=self.tasks_config["edit"],
            agent=self.editor(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the LatestAiDevelopment crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=self.verbose,
        )

    @before_kickoff
    def before_kickoff_function(self, inputs):
        click.secho(
            f"Team kicked off to analyze research on: {inputs['topic']} at {now}.",
            fg=m_colors.get("aqua"),
        )
        click.secho(f"Agents: {self.agents_config}", fg="green")
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


@click.command()
@click.option("--model_name", default="gpt-4o-mini", type=str, help="Model name")
@click.option("--temperature", default=0.7, type=float, help="Temperature")
@click.option("--topic", default="complexity science", type=str, help="Topic")
@click.option("--verbose", default=False, type=bool, is_flag=True, help="Verbosity")
def main(model_name, temperature, topic, verbose):
    ResearchTeam(
        model_name=model_name,
        temperature=temperature,
        verbose=verbose,
    ).crew().kickoff(inputs={"topic": topic})


if __name__ == "__main__":
    main()
