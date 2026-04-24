'''
config.py
this file contains configuration details for data collection for training the ML models
'''
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "metrics.csv")
EMIT_EVERY=10
