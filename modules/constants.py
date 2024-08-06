import os
import toml

def load_config():
    config_name = os.environ.get("AI_CONFIG", "default")
    config_path = os.path.join(os.path.dirname(__file__), f"../configs/{config_name}.toml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    
    with open(config_path, "r") as config_file:
        return toml.load(config_file)

# Load the active configuration
active_config = load_config()

# Set global constants based on the active configuration
globals().update(active_config)

# Helper function to get the active configuration
def get_active_config():
    return active_config
