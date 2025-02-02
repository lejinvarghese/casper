from agentarium import Agent
from src.utils.secrets import get_secret
from src.utils.logger import BaseLogger

OPEN_AI_API_KEY = get_secret("OPEN_AI_API_KEY")
logger = BaseLogger(__name__)


# Create some agents
alice_agent = Agent.create_agent(name="Alice", occupation="Software Engineer")
bob_agent = Agent.create_agent(name="Bob", occupation="Data Scientist")

alice_agent.talk_to(bob_agent, "Hello Bob! I heard you're working on some interesting data science projects.")
bob_agent.talk_to(alice_agent, "Hi Alice! Yes, I'm currently working on a machine learning model for natural language processing.")

alice_agent.act() # Let the agents decide what to do :D
bob_agent.act()

logger.info("Alice's interactions:")
logger.info(alice_agent.get_interactions())

logger.info("\nBob's interactions:")
logger.info(bob_agent.get_interactions())