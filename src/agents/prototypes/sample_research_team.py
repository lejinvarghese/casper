import os
import click
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from src.utils.secrets import get_secret

os.environ["OPENAI_API_KEY"] = get_secret("OPENAI_API_KEY")


@click.command()
@click.option("--model_name", default="gpt-3.5-turbo", help="Model name")
@click.option("--temperature", default=0.7, help="Temperature")
def main(model_name, temperature):
    click.secho("Welcome to the crew!", fg="blue")
    researcher = Agent(
        role="Senior Research Analyst",
        goal="Uncover cutting-edge developments in AI and data science",
        backstory="""You work at a leading tech think tank.
    Your expertise lies in identifying emerging trends.
    You have a knack for dissecting complex data and presenting actionable insights.""",
        verbose=True,
        allow_delegation=False,
        llm=ChatOpenAI(model_name=model_name, temperature=temperature),
    )

    writer = Agent(
        role="Tech Content Strategist",
        goal="Craft compelling content on tech advancements",
        backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
    You transform complex concepts into compelling narratives.""",
        verbose=True,
        allow_delegation=True,
        llm=ChatOpenAI(model_name=model_name, temperature=temperature),
    )

    critic = Agent(
        role="Blog critic",
        goal="Critic the writer's blog post",
        backstory="""Assume you're a machine learning engineer who is reviewing the blog post for technical accuracy and clarity, but you're also kind and supportive.""",
        verbose=True,
        allow_delegation=True,
        llm=ChatOpenAI(model_name=model_name, temperature=temperature),
    )

    task1 = Task(
        description="""Imagine a comprehensive analysis of the latest advancements in AI in 2024.
    Identify key trends, breakthrough technologies, and potential industry impacts.""",
        expected_output="Full analysis report in bullet points",
        agent=researcher,
    )

    task2 = Task(
        description="""Using the insights provided, develop an engaging blog
    post that highlights the most significant AI advancements.
    Your post should be informative yet accessible, catering to a tech-savvy audience.
    Make it sound cool, avoid complex words so it doesn't sound like AI.""",
        expected_output="A concise summary in more than 100 words.",
        agent=writer,
    )

    task3 = Task(
        description="""Using the insights provided, develop an engaging blog
    post that highlights the most significant AI advancements.
    Your post should be informative yet accessible, catering to a tech-savvy audience.
    Make it sound cool, avoid complex words so it doesn't sound like AI.""",
        expected_output="A critique that helps the writer improve content.",
        agent=critic,
    )

    crew = Crew(
        agents=[researcher, writer, critic],
        tasks=[task1, task2, task3],
        verbose=2,  # You can set it to 1 or 2 to different logging levels
        process=Process.sequential,
    )

    # Get your crew to work!
    result = crew.kickoff()

    click.secho(">" * 100, fg="yellow")
    click.secho(result, fg="green")


if __name__ == "__main__":
    main()
