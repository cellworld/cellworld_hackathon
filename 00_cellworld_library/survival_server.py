import time
from tcp_messages import MessageServiceServer
from environment import *
from cellworld_experiment_service import *
world_name = "21_05"


experiment_service = ExperimentService()

world_info = World_info("hexagonal", "canonical", world_name)

experiment_name = experiment_service.start_experiment(StartExperimentRequest("GAME", "", world_info, "PLAYERS", 10)).experiment_name

class SurvivalService:

    class Result:
        GoalReached = 1
        Capture = 2

    agent_ready_status = {"prey": False, "predator": False}
    process_thread = None

    # termination conditions:
    goal_location = Location(1, .5)
    goal_threshold = .05
    capture_radius = .1

    @staticmethod
    def __process__():
        print("Waiting for agents to be ready", end="")
        episode_count = 0
        while episode_count < 10:
            if SurvivalService.agent_ready_status["prey"] and SurvivalService.agent_ready_status["predator"]:
                episode_count += 1
                print()
                SurvivalService.agent_ready_status["prey"] = False
                SurvivalService.agent_ready_status["predator"] = False
                experiment_service.start_episode(StartEpisodeRequest(experiment_name=experiment_name))
                timer = Timer()
                SurvivalService.environment.start()
                print("starting episode")
                frame = 0
                while not SurvivalService.environment.complete:
                    SurvivalService.environment.step()
                    state = SurvivalService.environment.model.get_state()
                    time_stamp = timer.to_seconds()
                    prey_step = Step(time_stamp=time_stamp,
                                     agent_name="prey",
                                     frame=frame,
                                     location=state["prey"].location,
                                     rotation=state["prey"].theta * 180 / math.pi)
                    experiment_service.__process_step__(prey_step)
                    predator_step = Step(time_stamp=time_stamp,
                                         agent_name="predator",
                                         frame=frame,
                                         location=state["predator"].location,
                                         rotation=state["predator"].theta * 180 / math.pi)
                    experiment_service.__process_step__(predator_step)
                    # SurvivalService.environment.show()
                    frame += 1
                experiment_service.finish_episode(None)
                print("episode finished with result: ", SurvivalService.environment.result)
                SurvivalService.environment.stop()
            else:
                time.sleep(1)
                print(".", end="")
        experiment_service.finish_experiment(FinishExperimentRequest(experiment_name=experiment_name))
    @staticmethod
    def start():
        print("Initializing environment")
        # option 1: prey reach the goal
        SurvivalService.environment.add_termination_condition(
            lambda o: o["prey"].location.dist(SurvivalService.goal_location) <= SurvivalService.goal_threshold,
            SurvivalService.Result.GoalReached)
        # option 2: prey is capture by the predator
        SurvivalService.environment.add_termination_condition(
            lambda o: "predator" in o and o["predator"] and "prey" in o and o["prey"].location.dist(
                o["predator"].location) <= SurvivalService.capture_radius, SurvivalService.Result.Capture)

    world = World.get_from_world_info(world_info=world_info)
    paths_builder = Paths_builder.get_from_name(world_info.world_configuration,
                                                world_info.occlusions)
    environment = ChaseAndEvadeEnvironment(world,
                                           freq=100,
                                           real_time=True,
                                           visible=False)

    def agent_ready(self, agent_name: str):
        SurvivalService.agent_ready_status[agent_name] = True

    def set_action(self, agent_name: str, speed: float, turning: float):
        return SurvivalService.environment.set_action(agent_name=agent_name, speed=speed, turning=turning)

    def get_observation(self, agent_name: str):
        if SurvivalService.environment.complete:
            return JsonObject(complete=True)
        from cellworld import Timer
        t = Timer()
        state = SurvivalService.environment.get_observation(agent_name=agent_name)
        print (t.to_seconds())
        return state

    def get_world_info(self):
        return world_info


SurvivalService.start()

server = MessageServiceServer(SurvivalService)
server.start(9000)
SurvivalService.__process__()
