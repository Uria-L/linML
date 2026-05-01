'''
config.py
this file contains configuration details for data collection for training the ML models
'''
import os
from pathlib import Path
import yaml

config_file = Path(__file__).parent / "config.yaml"
with open(config_file, 'r', encoding="utf-8") as f:
    config_data = yaml.safe_load(f)

MODE = os.getenv('APP_MODE', config_data.get('mode', 'development'))

# env specific settings
env_config = config_data[MODE]

EMIT_EVERY = config_data['emit_every']
CSV_PATH = env_config['csv_path']
