import os
import yaml
from typing import Any

def load_yaml_config(path: str) -> dict[str, Any]:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_env_variable(key: str, default: Any = None) -> Any:
    return os.getenv(key, default) 