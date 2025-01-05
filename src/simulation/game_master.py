from warnings import filterwarnings

from concordia.agents.basic_agent import BasicAgent
from concordia.components.constant import ConstantComponent
from concordia.components.game_master.conversation import Conversation
from concordia.components.game_master.player_status import PlayerStatus
from concordia.components.game_master.direct_effect import DirectEffect
from concordia.components.game_master.relevant_events import RelevantEvents
from concordia.components.game_master.time_display import TimeDisplay
from concordia.environment.game_master import GameMaster
from concordia.language_model.language_model import LanguageModel

from src.simulation.memory import MemoryFactory
from src.simulation.utils import clock
from src.utils.logger import BaseLogger

filterwarnings("ignore")
logger = BaseLogger(__name__)


class GameMasterFactory:
    def __init__(
        self,
        memory_factory: MemoryFactory,
        agents: list[BasicAgent],
        model: LanguageModel,
    ):
        self.memory_factory = memory_factory
        self.associative_memory_factory = self.memory_factory.associative_memory_factory
        self.agents = agents
        self.model = model

    def build(self):
        components = self._get_components()
        return (
            GameMaster(
                model=self.model,
                memory=self.associative_memory_factory,
                clock=clock,
                players=self.agents,
                components=components,
                randomise_initiative=True,
                concurrent_action=True,
                player_observes_event=False,
                verbose=False,
            ),
            self.associative_memory_factory,
        )

    def _get_components(self):
        agent_status = PlayerStatus(
            clock_now=clock.now,
            model=self.model,
            memory=self.associative_memory_factory,
            player_names=[a.name for a in self.agents],
        )
        current_state = ConstantComponent(
            state="It is impossible to leave the Sundrop Saloon, since it is snowed in.",
            name="Fact",
        )
        shared_memories = ConstantComponent(state=" ".join(self.memory_factory.shared_memories), name="Background")

        convo_externality = Conversation(
            players=self.agents,
            model=self.model,
            memory=self.associative_memory_factory,
            clock=clock,
            burner_memory_factory=self.memory_factory.blank_memory_factory,
            components=[agent_status, current_state],
            cap_nonplayer_characters=3,
            shared_context=self.memory_factory.shared_context,
            verbose=False,
        )

        direct_effect_externality = DirectEffect(
            players=self.agents,
            model=self.model,
            memory=self.associative_memory_factory,
            clock_now=clock.now,
            verbose=False,
            components=[agent_status],
        )

        relevant_events = RelevantEvents(clock.now, self.model, self.associative_memory_factory)
        time_display = TimeDisplay(clock)

        return [
            agent_status,
            current_state,
            shared_memories,
            convo_externality,
            direct_effect_externality,
            relevant_events,
            time_display,
        ]
