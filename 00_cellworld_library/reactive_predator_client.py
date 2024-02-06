import time

from cellworld import *
from tcp_messages import MessageClient
from environment import ReactivePredator, AgentData
import sys

agent_name = "predator"

client = MessageClient()

if not client.connect("127.0.0.1", 9000):
    print("Fail to connect to game server")
    exit(1)

world_info = client.send_request("get_world_info").get_body(World_info)

world = World.get_from_world_info(world_info)

paths_builder = Paths_builder.get_from_name(world_info.world_configuration, world_info.occlusions)

predator_agent = ReactivePredator(world,
                                  ppath_builder=paths_builder,
                                  pvisibility=Location_visibility.from_world(world),
                                  pP_value=2,
                                  pI_value=0,
                                  pD_value=0,
                                  pmax_speed=1.5,
                                  pmax_turning_speed=math.pi)

visible = False

if visible:
    display = Display(world, fig_size=(10,10), animated=True)
    display.agent(agent_name="prey", location=Location(.5, .5), rotation=0, color="b")
    display.set_agent_marker(agent_name="prey", marker=Agent_markers.arrow())

    display.agent(agent_name="predator", location=Location(.5, .5), rotation=0, color="r")
    display.set_agent_marker(agent_name="predator", marker=Agent_markers.arrow())


for i in range(10):
    client.send_message("agent_ready", agent_name=agent_name)
    state = client.send_request("get_observation", agent_name=agent_name).get_body(JsonObject)
    print("Waiting for game to be ready", end="")
    while state.complete:
        time.sleep(1)
        print(".", end="")
        state = client.send_request("get_observation", agent_name=agent_name).get_body(JsonObject)
    print()
    print("Running game")
    while not state.complete:
        observation = state.observation
        if "prey" in observation and observation["prey"]:
            observation["prey"] = observation["prey"].into(AgentData)
        if "predator" in observation and observation["predator"]:
            observation["predator"] = observation["predator"].into(AgentData)
        # if "observation" in observation:
        #     for agent_name in observation.observation:
        #         agent_data = observation.observation[agent_name]
        #         if agent_data:
        #             display.agent(agent_name=agent_name,
        #                           location=agent_data.location,
        #                           rotation=to_degrees(agent_data.theta),
        #                           color=agent_data.color,
        #                           size=15)
        if visible:
            display.update()
        agent_action = predator_agent.get_action(observation)
        client.send_message("set_action", agent_name=agent_name, speed=agent_action.speed, turning=agent_action.turning_speed)
        state = client.send_request("get_observation", agent_name=agent_name).get_body(JsonObject)
    input("redy for another round?")
