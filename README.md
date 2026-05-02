# linML

linML aims to be the simplest way to use ML to protect a linux machine

it does so by collecting local data, and train multiple ML models to learn and protect the computer's normal usage

linML uses python for data collection and model training

the project has 3 main components:

1. data collector - collects data for training and for live monitoring of the system

2. ML hub - train ML models

3. detection engine - uses ML models for detection and response

# Requirements

Just Linux & python

# Quick start

1. clone the repo
2. install -r requirements.txt (use venv)
3. sudo python3 setup_collector.py
4. sudo python3 setup_engine.py

step 3 configures the data collector as a systemd service
step 4 trains the selected models, and starts the detection engine as a systemd service

# Methods

The following methods are currently supported:
- Endpoint binary behavior classification (iForest) - flags anomalous binaries
