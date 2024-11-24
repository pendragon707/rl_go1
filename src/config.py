ROBOT = "go1" # Robot name, "go2", "b2", "b2w", "h1", "go2w", "g1" 
ROBOT_SCENE = "submodules/unitree_mujoco/unitree_robots/" + ROBOT + "/scene.xml" # Robot scene
DOMAIN_ID = 1 # Domain id

SIMULATE_DT = 0.0025  # Need to be larger than the runtime of viewer.sync()
VIEWER_DT = 0.02  # 50 fps for viewer

SEND_STATE_DT = 0.01 # Send state to client
COMMAND_RESET_TIMEOUT = 0.1

ENABLE_SIMULATION = True