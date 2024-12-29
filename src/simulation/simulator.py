# @title Imports

import collections
import concurrent.futures
import datetime

import matplotlib.pyplot as plt
import numpy as np
from sentence_transformers import SentenceTransformer

from concordia.agents import basic_agent

# from concordia.components.agent import to_be_deprecated as components
from concordia import components as generic_components
from concordia.associative_memory import associative_memory
from concordia.associative_memory import blank_memories
from concordia.associative_memory import formative_memories
from concordia.associative_memory import importance_function
from concordia.clocks import game_clock
from concordia.components import game_master as gm_components
from concordia.environment import game_master
from concordia.metrics import goal_achievement
from concordia.metrics import common_sense_morality
from concordia.metrics import opinion_of_others
from concordia.utils import html as html_lib
from concordia.utils import measurements as measurements_lib
from concordia.utils import plotting
from llama_cpp.llama_cpp import llama_free_model

from src.constants import EMBEDDING_MODEL_NAME
from src.models import EmbeddingModel, SimulationModel

from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)

model = SimulationModel()
# emb = EmbeddingModel().model
st_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
embedder = lambda x: st_model.encode(x, show_progress_bar=False)

choice_response = model.sample_choice(
    "What comes next? a,b,c,d,e,f,", responses=["d", "g", "z"]
)
logger.info(f"Sample response: {choice_response[1]}")

text_response = model.sample_text("What is the meaning of life?", max_tokens=40)
logger.info(f"Text response: {text_response}")
