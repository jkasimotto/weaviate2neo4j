import os
import yaml

def read_config(file_path):
    with open(file_path, 'r') as stream:
        config = yaml.safe_load(stream)
    for key, value in config.items():
        for subkey in value.keys():
            env_key = f"{key.upper()}_{subkey.upper()}"
            if env_key in os.environ:
                config[key][subkey] = os.environ[env_key]
    return config