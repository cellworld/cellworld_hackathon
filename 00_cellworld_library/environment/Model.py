from threading import Thread
from cellworld import *
from .Agent import Agent, AgentData, AgentAction


class Model:

    def __init__(self,
                 world: World,
                 freq: int = 100,
                 real_time: bool = False,
                 visible: bool = True):
        self.visible = visible
        self.real_time = real_time
        self.world = world
        self.agents = dict()
        self.agents_data = JsonObject()
        if self.visible:
            self.display = Display(self.world,
                                   animated=True,
                                   fig_size=(6, 6))
        self.thread = None
        self.running = False
        self.interval = 1 / freq
        self.last_update = Timer(self.interval)
        self.arena_polygon = Polygon(self.world.implementation.space.center, 6,
                                     self.world.implementation.space.transformation.size / 2,
                                     self.world.implementation.space.transformation.rotation)
        self.occlusions_polygons = Polygon_list.get_polygons(
            Location_list(iterable=[c.location for c in self.world.cells.occluded_cells()]), 6,
            self.world.implementation.cell_transformation.size / 2 * 1.05,
            self.world.implementation.cell_transformation.rotation)
        self.visibility = Location_visibility(occlusions=self.occlusions_polygons)

    def is_valid_location(self, agent_location: Location):
        if self.arena_polygon.contains(agent_location):
            for p in self.occlusions_polygons:
                if p.contains(agent_location):
                    return False
            return True
        else:
            return False

    def run(self):
        self.running = True
        self.thread = Thread(target=self.__process__)
        self.thread.start()

    def __move_agent__(self, agent_name):
        agent = self.agents_data[agent_name]
        agent.theta = normalize(agent.theta + agent.turning_speed * self.interval)
        new_location = Location(agent.location.x, agent.location.y)
        new_location.move(theta=agent.theta, dist=agent.speed * self.interval)
        if self.is_valid_location(new_location):
            self.agents_data[agent_name].location = new_location

    def stop(self):
        if self.thread:
            self.running = False
            self.thread.join()

    def __process__(self):
        import time
        t = Timer(self.interval)
        while self.running:
            t.reset()
            self.step()
            if self.real_time:
                pending_wait = self.interval - t.to_seconds()
                if pending_wait > 0:
                    time.sleep(pending_wait)

    def step(self):
        while not self.last_update.time_out():
            pass
        for agent_name in self.agents.keys():
            if self.agents_data[agent_name].auto_update:
                action = self.agents[agent_name].get_action(self.get_observation(agent_name))
                self.agents_data[agent_name].speed = action.speed
                self.agents_data[agent_name].turning_speed = action.turning_speed
        for agent_name in self.agents.keys():
            self.__move_agent__(agent_name)
        self.last_update = Timer(self.interval)

    def set_agent_action(self, agent_name: str, action: AgentAction):
        self.agents_data[agent_name].speed = action.speed
        self.agents_data[agent_name].turning_speed = action.turning_speed

    def __create_observation__(self, agent_name: str) -> JsonObject:
        observation = JsonObject()
        src = self.agents_data[agent_name].location
        for dst_agent_name in self.agents_data:
            dst_agent_data = self.agents_data[dst_agent_name]
            if self.visibility.is_visible(src, dst_agent_data.location):
                observation[dst_agent_name] = dst_agent_data
            else:
                observation[dst_agent_name] = None
        return observation

    def get_state(self):
        return self.agents_data

    def get_observation(self, agent_name: str) -> JsonObject:
        return self.__create_observation__(agent_name)

    def show(self):
        if not self.visible:
            return

        for agent_name in self.agents_data:
            agent_data = self.agents_data[agent_name]
            self.display.agent(agent_name=agent_name,
                               location=agent_data.location,
                               rotation=to_degrees(agent_data.theta),
                               color=agent_data.color,
                               size=15)
        self.display.update()

    def set_agent_position(self, agent_name: str,
                           location: Location,
                           theta: float):
        self.agents_data[agent_name].location = location
        self.agents_data[agent_name].theta = theta

    def add_agent(self,
                  agent_name: str,
                  agent: Agent,
                  theta: float,
                  location: Location = Location(0, 0),
                  color: str = "b",
                  auto_update: bool = True):
        self.agents[agent_name] = agent
        self.agents_data[agent_name] = AgentData(location=location,
                                                 theta=theta,
                                                 speed=0,
                                                 turning_speed=0,
                                                 color=color,
                                                 auto_update=auto_update)
        if not self.visible:
            return
        self.display.set_agent_marker(agent_name, Agent_markers.arrow())
