from transformers.agents import HfEngine, ReactJsonAgent
from warnings import filterwarnings
from src.language.utils.logger import BaseLogger
from src.language.utils.tools import RetrieverTool
from src.language.storage import FaissVectorStore
from src.language.constants import AGENT_MODEL


filterwarnings("ignore")
logger = BaseLogger(__name__)
llm_engine = HfEngine(AGENT_MODEL)
db, sources = FaissVectorStore().create()

agent = ReactJsonAgent(tools=[RetrieverTool(db, sources)], llm_engine=llm_engine)

agent_output = agent.run("Show me a finetuning script for embeddings.")
logger.info(f"Final output: {agent_output}")
