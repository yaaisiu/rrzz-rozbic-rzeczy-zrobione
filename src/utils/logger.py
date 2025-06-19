import logging
import yaml

with open('config/logging_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rrzz-rozbic-rzeczy-zrobione") 