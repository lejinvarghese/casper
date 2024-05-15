from transformers.agents import ReactJsonAgent
from warnings import filterwarnings
from src.language.utils.logger import BaseLogger
from src.language.utils.tools import RetrieverTool
from src.language.storage import FaissVectorStore
from src.language.models import AgentModel


filterwarnings("ignore")
logger = BaseLogger(__name__)
llm = AgentModel()
vs = FaissVectorStore()
agent = ReactJsonAgent(tools=[RetrieverTool(vs.db, vs.sources)], llm_engine=llm.model)

agent_output = agent.run("Show me a finetuning script for embeddings.")
logger.info(f"Final output: {agent_output}")
