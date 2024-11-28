from yaml import load, SafeLoader
from agent_config import AgentConfig

class Agent:

    def __init__(config_path: Optional[Path] = None): 
        if config_path:       
            self.load_config(config_path)
        else:
            self.config = AgentConfig()

    def load_config(path: Path):
        loaded = load(yaml, Loader=SafeLoader)
        self.config = AgentConfig(**loaded)

    
