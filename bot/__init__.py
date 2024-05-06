import logging.config
import os

import yaml

logs_path = "../Logs"
logger_config_file_path = "config_data/logging_config.yaml"

if not os.path.exists(os.path.join(os.path.dirname(__file__), logs_path)):
    os.makedirs(os.path.join(os.path.dirname(__file__), logs_path))

with open(os.path.join(os.path.dirname(__file__), logger_config_file_path), "rt") as f:
    logging_config = yaml.safe_load(f.read())
logging.config.dictConfig(logging_config)
