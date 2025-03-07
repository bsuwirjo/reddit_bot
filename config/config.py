import yaml

def load_config(filepath="config/config.yaml"):
    """
    Load configuration from a YAML file.
    """
    with open(filepath, 'r') as f:
        config = yaml.safe_load(f)
    return config
