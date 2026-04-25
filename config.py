'''
config.py
this file contains configuration details for data collection for training the ML models
'''
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMIT_EVERY=10

# check if running as systemd service
if os.getenv('TELEMETRY_MODE') == 'system':
    CSV_PATH = "/var/log/telemetry/metrics.csv"
else:
    CSV_PATH = os.path.join(BASE_DIR, "data", "metrics.csv")
