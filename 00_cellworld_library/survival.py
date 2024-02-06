from tcp_messages import MessageServiceServer
from gamepad import *
from environment import *

g = GamePad()


turn = float(0)
speed = float(0)

def hturn(v):
    global turn
    turn = float(v / 32767)


def hspeed(v):
    global speed
    speed = -float(v / 32767)


g.add_handler(UpdateType.Axis, 0, hturn)
g.add_handler(UpdateType.Axis, 1, hspeed)

world_name = "21_05"



class Result:
    GoalReached = 1
    Capture = 2

world = World.get_from_parameters_names("hexagonal", "canonical", world_name)
paths_builder = Paths_builder.get_from_name("hexagonal", world_name)
predator_agent = Predator(world,
                          ppath_builder=paths_builder,
                          pvisibility=Location_visibility.from_world(world),
                          pP_value=2,
                          pI_value=0,
                          pD_value=0,
                          pmax_speed=1.5,
                          pmax_turning_speed=math.pi)


environment = ChaseAndEvadeEnvironment(world,
                                       freq=100,
                                       real_time=False,
                                       predator_agent=predator_agent)

#termination conditions:
goal_location = Location(1, .5)
goal_threshold = .05
capture_radius = .1

#option 1: prey reach the goal
environment.add_termination_condition(lambda o: o["prey"].location.dist(goal_location) <= goal_threshold, Result.GoalReached)
#option 2: prey reach the goal
environment.add_termination_condition(lambda o: "predator" in o and o["predator"] and "prey" in o and o["prey"].location.dist(o["predator"].location) <= capture_radius, Result.Capture)


counter = 0
for i in range(20):
    #runs the environment
    environment.start()

    #loops until the predator captures the prey or the prey reaches the goal
    while not environment.complete:
        g.update()
        #starts a timer
        t = Timer()
        #reads an observation from the environment.
        #sets an action for the prey
        #speed float in habitat lengths per second.
        #turning float in radians per second
        pre_o = environment.get_observation(agent_name="prey")
        environment.set_action(agent_name="prey", speed=speed, turning=turn)
        environment.step()
        post_o = environment.get_observation(agent_name="prey")
        counter += 1
        # if counter % 100 == 0 :
        environment.show()
        # computes the remaining time for 1/10 of a second to make the action interval consistent.
        # observation format: Tuple
        # [prey location, prey theta, goal location, predator location, predator theta, captured, goal_reached]
        # prey location: Type Location
        # prey theta: Type float in radians
        # goal location: Type Location
        # predator location: Type Location (None when predator is not visible)
        # predator theta: Type float in radians (None when predator is not visible)
        # captured: Type boolean : Prey has been captured by the predator. environment.complete becomes true.
        # goal_reached : Type boolean : Prey reached the goal location. environment.complete becomes true.
        # stops the environment

    environment.stop()

