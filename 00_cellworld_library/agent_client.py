import time
from cellworld import *
from tcp_messages import MessageClient
from gamepad import *
import sys

agent_name = sys.argv[1]
gamepad = GamePad()

turn = float(0)
speed = float(0)

def hturn(v):
    global turn
    turn = float(v / 32767)


def hspeed(v):
    global speed
    speed = -float(v / 32767)


gamepad.add_handler(UpdateType.Axis, 0, hturn)
gamepad.add_handler(UpdateType.Axis, 1, hspeed)



client = MessageClient()
if not client.connect("127.0.0.1", 9000):
    print("Fail to connect to game server")
    exit(1)

world_info = client.send_request("get_world_info").get_body(World_info)

world = World.get_from_world_info(world_info)

display = Display(world, fig_size=(10,10), animated=True)

#add the two markers for the agents
display.agent(agent_name="prey", location=Location(-100, -100), rotation=0, color="b")
display.set_agent_marker(agent_name="prey", marker=Agent_markers.arrow())

display.agent(agent_name="predator", location=Location(-100, -100), rotation=0, color="r")
display.set_agent_marker(agent_name="predator", marker=Agent_markers.arrow())


for i in range(10):
    client.send_message("agent_ready", agent_name=agent_name)
    observation = client.send_request("get_observation", agent_name=agent_name).get_body(JsonObject)
    print("Waiting for game to be ready", end="")
    while observation.complete:
        time.sleep(1)
        print(".", end="")
        observation = client.send_request("get_observation", agent_name=agent_name).get_body(JsonObject)
    print()
    print("Running game")
    while not observation.complete:
        if "observation" in observation:
            for agent_name in observation.observation:
                agent_data = observation.observation[agent_name]
                if agent_data:
                    display.agent(agent_name=agent_name,
                                  location=agent_data.location,
                                  rotation=to_degrees(agent_data.theta),
                                  color=agent_data.color,
                                  size=15)
        display.update()
        gamepad.update()
        client.send_message("set_action", agent_name=agent_name, speed=speed, turning=turn)

        timer = Timer()
        observation_json = client.send_request("get_observation", agent_name=agent_name)
        print (timer.to_seconds())
        observation = observation_json.get_body(JsonObject)
    input("redy for another round?")
