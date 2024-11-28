from dataclasses import dataclass

@dataclass
class AgentConfig:
    ROBOT: str = "go1"
    ROBOT_SCENE: str = "submodules/unitree_mujoco/unitree_robots/" + ROBOT + "/scene.xml" # Robot scene
    DOMAIN_ID: int = 1 # Domain id

    SIMULATE_DT: float = 0.0025  # Need to be larger than the runtime of viewer.sync()
    VIEWER_DT: float = 0.02  # 50 fps for viewer

    SEND_STATE_DT: float = 0.001 # Send state to client
    COMMAND_RESET_TIMEOUT: float = 0.1

    ENABLE_SIMULATION: bool = True