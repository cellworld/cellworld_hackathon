from .Agent import *
from .Model import Model
from cellworld import *


class ChaseAndEvadeEnvironment:
    def __init__(self,
                 world: World,
                 freq: int = 100,
                 real_time: bool = True,
                 prey_agent: Agent = None,
                 predator_agent: Agent = None,
                 visible: bool = True):
        self.complete = True
        self.result = None
        self.world = world
        self.model = Model(world=self.world, freq=freq, real_time=real_time, visible=visible)
        self.goal_location = Location(1, .5)
        self.start_location = Location(0, .5)
        self.goal_threshold = self.world.implementation.cell_transformation.size / 2
        self.capture_threshold = self.world.implementation.cell_transformation.size
        self.prey = prey_agent
        self.model.add_agent("prey",
                             agent=self.prey,
                             theta=0,
                             color="b",
                             auto_update=self.prey is not None)
        self.predator = None
        self.termination_conditions = []
        self.predator = predator_agent

        # predator spawn locations are cells that are not visible from the
        # prey start location
        self.spawn_locations = Location_list()
        for c in self.world.cells.free_cells():
            if not self.model.visibility.is_visible(self.start_location, c.location):
                self.spawn_locations.append(c.location)
        self.model.add_agent("predator",
                             agent=self.predator,
                             theta=0,
                             color="r",
                             auto_update=self.predator is not None)

    def add_termination_condition(self, termination_condition, result):
        self.termination_conditions.append((termination_condition, result))

    def get_observation(self, agent_name: str) -> JsonObject:
        return JsonObject(observation=self.model.get_observation(agent_name),
                          complete=self.complete,
                          result=self.result)

    def is_complete(self):
        return self.complete

    def set_action(self, agent_name: str,  speed: float, turning: float) -> None:
        self.model.set_agent_action(agent_name, AgentAction(speed, turning))

    def run(self) -> None:
        self.start()
        self.model.run()

    def start(self) -> None:
        import random
        self.complete = False
        self.result = None
        self.model.set_agent_position("prey", self.start_location, math.pi / 2)
        predator_location = random.choice(self.spawn_locations)
        predator_theta = math.pi * 2 * random.random()
        self.model.set_agent_position("predator", predator_location, predator_theta)

    def step(self) -> None:
        if not self.complete:
            self.model.step()
            o = self.model.get_state()
            self.complete = False
            self.result = None
            for tc, r in self.termination_conditions:
                if tc(o):
                    self.complete = True
                    self.result = r

    def stop(self) -> None:
        self.model.stop()

    def show(self) -> None:
        self.model.show()
