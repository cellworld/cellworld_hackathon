from cellworld import *


class AgentAction(JsonObject):
    def __init__(self, speed: float = 0, turning_speed: float = 0):
        self.speed = speed
        self.turning_speed = turning_speed*10


class AgentData(JsonObject):

    def __init__(self,
                 location: Location = None,
                 theta: float = 0.0,
                 speed: float = 0.0,
                 turning_speed: float = 0.0,
                 color: str = "b",
                 auto_update=True):
        if location:
            self.location = location
        else:
            self.location = Location(0,0)
        self.theta = theta
        self.speed = speed
        self.turning_speed = turning_speed
        self.color = color
        self.auto_update = auto_update


class Agent:

    def get_action(self, observation: dict) -> AgentAction:
        return AgentAction(0, 0)
