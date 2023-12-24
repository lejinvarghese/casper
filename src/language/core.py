"""
Core abstract functionalities.
"""
from abc import ABC, abstractmethod, property

class Agent(ABC):
    """
    Abstract class for an agent.
    """

    @property
    def role(self):
        pass

    @property
    def objective(self):
        pass

    @property
    def max_radius(self):
        pass

    @abstractmethod
    def respond(self):
        pass


class Researcher(Agent):
    pass

    @property
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


class Connector:
    pass

class QueryEngine:
    pass

class Chat:
    pass

class KnowledgeGraphCreator:
    """https://docs.llamaindex.ai/en/stable/examples/query_engine/knowledge_graph_query_engine.html"""
    pass