# @title Imports


import collections
from tqdm import tqdm
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
from warnings import filterwarnings
from concordia.language_model import gpt_model


from src.models.embeddings import EmbeddingModelAdapter

from src.utils.logger import BaseLogger
from src.utils.secrets import get_secret

filterwarnings("ignore")
logger = BaseLogger(__name__)

# model = SimulationModelAdapter(n_gpu_layers=100)

OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"
# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
model = gpt_model.GptLanguageModel(api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)
st_model = EmbeddingModelAdapter().model
embedder = lambda x: st_model._embed(x)

text_response = model.sample_text("What is the meaning of life?", max_tokens=40)
logger.info(f"Text response: {text_response}")

# make the clock
time_step = datetime.timedelta(minutes=20)
SETUP_TIME = datetime.datetime(hour=20, year=2024, month=10, day=1)

START_TIME = datetime.datetime(hour=19, year=2024, month=10, day=2)
clock = game_clock.MultiIntervalClock(
    start=SETUP_TIME, step_sizes=[time_step, datetime.timedelta(minutes=10)]
)

# Importance models
importance_model = importance_function.AgentImportanceModel(model)
importance_model_gm = importance_function.ConstantImportanceModel()

# shared memories
shared_memories = [
    "There is a pub called The Sundrop Saloon.",
    "Alice stole Bob's car and crashed it.",
    (
        "Alice, Bob, Charlie and Dorothy always spend their evenings at the "
        + "Sundrop Saloon."
    ),
]

# The generic context will be used for the NPC context. It reflects general
# knowledge and is possessed by all characters.
shared_context = model.sample_text(
    "Summarize the following passage in a concise and insightful fashion:\n"
    + "\n".join(shared_memories)
    + "\n"
    + "Summary:"
)
logger.info(f"{shared_context}\n")

# memory factory
blank_memory_factory = blank_memories.MemoryFactory(
    model=model,
    embedder=embedder,
    importance=importance_model.importance,
    clock_now=clock.now,
)

formative_memory_factory = formative_memories.FormativeMemoryFactory(
    model=model,
    shared_memories=shared_memories,
    blank_memory_factory_call=blank_memory_factory.make_blank_memory,
)

# Creating character backgrounds, goals and traits. Modify to explore how it influences the outcomes
NUM_PLAYERS = 2

scenario_premise = [
    (
        "Alice, Bob, Charlie and Dorothy are at the Sundrop Saloon. There "
        + "is a snow storm and they have to wait it out inside."
    ),
]
player_configs = [
    formative_memories.AgentConfig(
        name="Alice",
        gender="female",
        goal="Alice wants Bob to accept his car is trashed and back off.",
        context=shared_context,
        traits="responsibility: low; aggression: high, empathy: medium",
    ),
    formative_memories.AgentConfig(
        name="Bob",
        gender="male",
        goal="Bob wants Alice to pay for his car.",
        context=shared_context,
        traits="responsibility: high; aggression: low",
    ),
    formative_memories.AgentConfig(
        name="Charlie",
        gender="male",
        goal="Charlie wants Alice to apologise.",
        context=shared_context,
        traits="responsibility: low; aggression: high",
    ),
    formative_memories.AgentConfig(
        name="Dorothy",
        gender="female",
        goal=(
            "Dorothy wants to create a conflict between Bob and Alice, because"
            " it is funny."
        ),
        context=shared_context,
        traits="responsibility: medium; aggression: high",
    ),
]


def build_agent(
    agent_config,
    player_names: list[str],
    measurements: measurements_lib.Measurements | None = None,
):

    mem = formative_memory_factory.make_memories(agent_config)

    agent_name = agent_config.name
    instructions = generic_components.constant.ConstantComponent(
        state=(
            f"The instructions for how to play the role of {agent_name} are as "
            "follows. This is a social science experiment studying how well you "
            f"play the role of a character named {agent_name}. The experiment "
            "is structured as a tabletop roleplaying game (like dungeons and "
            "dragons). However, in this case it is a serious social science "
            "experiment and simulation. The goal is to be realistic. It is "
            f"important to play the role of a person like {agent_name} as "
            f"accurately as possible, i.e., by responding in ways that you think "
            f"it is likely a person like {agent_name} would respond, and taking "
            f"into account all information about {agent_name} that you have. "
            "Always use third-person limited perspective."
        ),
        name="role playing instructions\n",
    )

    time = generic_components.report_function.ReportFunction(
        name="Current time",
        function=clock.current_time_interval_str,
    )

    current_obs = generic_components.agent.observation.Observation(
        agent_name=agent_config.name,
        clock_now=clock.now,
        memory=mem,
        timeframe=clock.get_step_size(),
        component_name="current observations",
    )
    summary_obs = generic_components.agent.observation.ObservationSummary(
        agent_name=agent_config.name,
        model=model,
        clock_now=clock.now,
        memory=mem,
        components=[current_obs],
        timeframe_delta_from=datetime.timedelta(hours=4),
        timeframe_delta_until=datetime.timedelta(hours=1),
        component_name="summary of observations",
    )

    self_perception = generic_components.agent.self_perception.SelfPerception(
        name=f"answer to what kind of person is {agent_config.name}",
        model=model,
        memory=mem,
        agent_name=agent_config.name,
        clock_now=clock.now,
    )
    situation_perception = (
        generic_components.agent.situation_perception.SituationPerception(
            name=(
                f"answer to what kind of situation is {agent_config.name} in "
                + "right now"
            ),
            model=model,
            memory=mem,
            agent_name=agent_config.name,
            components=[current_obs, summary_obs],
            clock_now=clock.now,
        )
    )
    person_by_situation = (
        generic_components.agent.person_by_situation.PersonBySituation(
            name=(
                f"answer to what would a person like {agent_config.name} do in a "
                + "situation like this"
            ),
            model=model,
            memory=mem,
            agent_name=agent_config.name,
            clock_now=clock.now,
            components=[self_perception, situation_perception],
            verbose=False,
        )
    )

    initial_goal_component = generic_components.constant.ConstantComponent(
        state=agent_config.goal
    )

    persona = generic_components.sequential.Sequential(
        name="persona",
        components=[
            self_perception,
            situation_perception,
            person_by_situation,
            initial_goal_component,
        ],
    )

    goal_metric = goal_achievement.GoalAchievementMetric(
        model=model,
        player_name=agent_config.name,
        player_goal=agent_config.goal,
        clock=clock,
        name="Goal Achievement",
        measurements=measurements,
        channel="goal_achievement",
        verbose=False,
    )
    morality_metric = common_sense_morality.CommonSenseMoralityMetric(
        model=model,
        player_name=agent_config.name,
        clock=clock,
        name="Morality",
        verbose=False,
        measurements=measurements,
        channel="common_sense_morality",
    )
    agent = basic_agent.BasicAgent(
        model,
        memory=mem,
        agent_name=agent_config.name,
        clock=clock,
        verbose=False,
        components=[
            instructions,
            persona,
            time,
            current_obs,
            goal_metric,
            morality_metric,
        ],
        update_interval=time_step,
    )
    reputation_metric = opinion_of_others.OpinionOfOthersMetric(
        model=model,
        player_name=agent_config.name,
        player_names=player_names,
        context_fn=agent.state,
        clock=clock,
        name="Opinion",
        verbose=False,
        measurements=measurements,
        channel="opinion_of_others",
        question="What is {opining_player}'s opinion of {of_player}?",
    )
    agent.add_component(reputation_metric)
    return agent, mem


player_configs = player_configs[:NUM_PLAYERS]
player_names = [player.name for player in player_configs][:NUM_PLAYERS]
measurements = measurements_lib.Measurements()

players = []
memories = {}

logger.info(f"Players: {player_names}")
for config in player_configs[:NUM_PLAYERS]:
    agent, mem = build_agent(config, player_names, measurements)
    players.append(agent)
    memories[agent.name] = mem

# with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_PLAYERS) as pool:
#     for agent, mem in pool.map(
#         build_agent,
#         player_configs[:NUM_PLAYERS],
#         # All players get the same `player_names`.
#         [player_names] * NUM_PLAYERS,
#         # All players get the same `measurements` object.
#         [measurements] * NUM_PLAYERS,
#     ):
#         players.append(agent)
#         memories[agent.name] = mem

game_master_memory = associative_memory.AssociativeMemory(
    sentence_embedder=embedder,
    importance=importance_model_gm.importance,
    clock=clock.now,
)

player_names = [player.name for player in players]

snowed_in_construct = generic_components.constant.ConstantComponent(
    state=("It is impossible to leave the Sundrop Saloon, since it is snowed in."),
    name="Fact",
)
scenario_knowledge = generic_components.constant.ConstantComponent(
    state=" ".join(shared_memories), name="Background"
)

player_status = gm_components.player_status.PlayerStatus(
    clock_now=clock.now,
    model=model,
    memory=game_master_memory,
    player_names=player_names,
)


convo_externality = gm_components.conversation.Conversation(
    players=players,
    model=model,
    memory=game_master_memory,
    clock=clock,
    burner_memory_factory=blank_memory_factory,
    components=[player_status, snowed_in_construct],
    cap_nonplayer_characters=3,
    shared_context=shared_context,
    verbose=False,
)

direct_effect_externality = gm_components.direct_effect.DirectEffect(
    players=players,
    model=model,
    memory=game_master_memory,
    clock_now=clock.now,
    verbose=False,
    components=[player_status],
)

relevant_events = gm_components.relevant_events.RelevantEvents(
    clock.now, model, game_master_memory
)
time_display = gm_components.time_display.TimeDisplay(clock)

env = game_master.GameMaster(
    model=model,
    memory=game_master_memory,
    clock=clock,
    players=players,
    components=[
        snowed_in_construct,
        scenario_knowledge,
        player_status,
        convo_externality,
        direct_effect_externality,
        relevant_events,
        time_display,
    ],
    randomise_initiative=True,
    concurrent_action=True,
    player_observes_event=False,
    verbose=False,
)

clock.set(START_TIME)

logger.info("Adding scenario premise to the game master memory\n")
for premise in scenario_premise:
    game_master_memory.add(premise)
    for player in players:
        player.observe(premise)

logger.info(f"Starting the simulation at {clock.now()}\n")
episode_length = 1
env.run_episode(max_steps=episode_length)

# plot the results
player_logs = []
player_log_names = []
for player in players:
    name = player.name
    detailed_story = "\n".join(
        memories[player.name].retrieve_recent(k=1000, add_time=True)
    )
    summary = ""
    summary = model.sample_text(
        f"Sequence of events that happened to {name}:\n{detailed_story}"
        "\nWrite a short story that summarises these events.\n",
        max_tokens=3500,
        terminators=(),
    )

    all_player_mem = memories[player.name].retrieve_recent(k=1000, add_time=True)
    all_player_mem = ["Summary:", summary, "Memories:"] + all_player_mem
    player_html = html_lib.PythonObjectToHTMLConverter(all_player_mem).convert()
    player_logs.append(player_html)
    player_log_names.append(f"{name}")
    data = (
        memories[player.name]
        .get_data_frame()
        .drop(columns=["embedding"])
        .sort_values(["time", "importance"], ascending=True)
    )
    file_name = f"./src/data/.simulation/logs_{str.lower(name)}.csv"
    data.to_csv(file_name)
    file_name = file_name.replace(".csv", ".html")
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(player_html)
    logger.warning(f"HTML file saved as {file_name}")
