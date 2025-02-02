from dotenv import load_dotenv
from agentarium import Agent

from src.utils.logger import BaseLogger

load_dotenv()
logger = BaseLogger(__name__)

if __name__ == "__main__":

    agent_profiles = {
        "Alice": {"occupation": "Software Engineer"},
        "Bob": {"occupation": "Data Scientist"},
        "Cassia": {"occupation": "Machine Learning Engineer"},
    }
    agents = {}
    for name, profile in agent_profiles.items():
        agents[name] = Agent.create_agent(name=name, occupation=profile.get("occupation"))
        logger.debug(f"Created agent: {name}, ID: {agents[name].agent_id}")

    def agent_conversation(n_rounds=3):
        conversations = [
            ("Alice", "Bob", "Hey Bob, what are you working on?"),
            ("Bob", "Cassia", "Cassia, any thoughts on NLP models?"),
            ("Cassia", "Alice", "Alice, how do you optimize large-scale applications?"),
        ]

        for _ in range(n_rounds):
            for sender, receiver, message in conversations:
                logger.debug(
                    f"{sender} (ID: {agents[sender].agent_id}) → {receiver} (ID: {agents[receiver].agent_id})"
                )
                try:
                    agents[sender].talk_to(agents[receiver], message)
                    agents[sender].act()
                except Exception as e:
                    logger.error(f"Error: {e}")
                    continue

    agent_conversation(n_rounds=3)
    for name, agent in agents.items():
        logger.info(f"\n{name}'s interactions:")
        logger.info(agent.get_interactions())