"""
Core abstract functionalities.
"""
from abc import ABC, abstractmethod, abstractproperty


class Agent(ABC):
    """
    Abstract class for an agent.
    """

    @abstractproperty
    def role(self):
        pass

    @abstractproperty
    def objective(self):
        pass

    @abstractmethod
    def respond(self):
        pass


class Researcher(Agent):
    pass

    @abstractproperty
    def subject(self):
        pass


class Integrator(Researcher):
    pass


class Assistant(Agent):
    pass


class Delegator(Agent):
    pass


class Integrator(Researcher):
    pass


class Connector(ABC):
    @abstractproperty
    def source(self):
        pass

    @abstractproperty
    def destination(self):
        pass


class QueryEngine:
    pass


class Chat:
    pass


class KnowledgeGraphCreator:
    """https://docs.llamaindex.ai/en/stable/examples/query_engine/knowledge_graph_query_engine.html"""

    pass
