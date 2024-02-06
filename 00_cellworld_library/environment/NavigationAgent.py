from .Agent import *


class NavigationAgent(Agent):
    def __init__(self,
                 pworld: World,
                 ppath_builder: Paths_builder,
                 pvisibility: Location_visibility,
                 agent_name: str,
                 pP_value: float = .1,
                 pI_value: float = .1,
                 pD_value: float = .1,
                 pmax_speed: float = .4,
                 pmax_turning_speed: float = .2):
        from cellworld import Location, Paths
        self.agent_name = agent_name
        self.world = pworld
        self.paths = Paths(ppath_builder, pworld)
        self.visibility = pvisibility
        self.destination = None
        self.destination_cell = None
        self.P_value = pP_value
        self.I_value = pI_value
        self.D_value = pD_value
        self.last_theta = None
        self.accum_theta_error = 0
        self.max_speed = pmax_speed
        self.max_turning_speed = pmax_turning_speed
        self.reached = True

    def set_destination_cell(self, cell_id: int):
        self.destination_cell = self.world.cells[cell_id]
        self.reached = False

    def __update_destination__(self, agent_location: Location):
        if self.destination_cell and \
                agent_location.dist(self.destination_cell.location) < self.world.implementation.cell_transformation.size / 2:
            self.reached = True #has reached the destination cell
        predator_cell = self.world.cells[self.world.cells.find(agent_location)]
        self.path = self.paths.get_path(predator_cell, self.destination_cell)
        for cd in self.path:
            if self.visibility.is_visible(agent_location, cd.location):
                self.destination = cd.location

    @staticmethod
    def normalized_error(theta_error: float):
        pi_err = math.pi * theta_error / 2
        return 1 / (pi_err * pi_err + 1)

    def get_action(self, observation: dict) -> AgentAction:
        if self.reached:
            return AgentAction(0, 0)
        agent = observation[self.agent_name]
        self.__update_destination__(agent.location)
        desired_theta = agent.location.atan(self.destination)
        theta_error, direction = angle_difference(agent.theta, desired_theta)
        dist_error = agent.location.dist(self.destination)
        self.accum_theta_error += theta_error
        turning_speed_P = theta_error * self.P_value
        turning_speed_D = 0
        if self.last_theta is not None:
            turning_speed_D = (self.last_theta - agent.theta) * self.D_value
        turning_speed_I = self.accum_theta_error * self.I_value
        turning_speed = turning_speed_P - turning_speed_D + turning_speed_I
        if turning_speed > self.max_turning_speed:
            turning_speed = self.max_turning_speed
        turning_speed = turning_speed * (-direction)
        speed = self.normalized_error(theta_error) * (1 + dist_error)
        if speed > self.max_speed:
            speed = self.max_speed
        self.last_theta = agent.theta
        return AgentAction(speed, turning_speed)