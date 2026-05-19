# linML

linML aims to be the simplest way to use ML to protect a linux machine

it does so by collecting local data, and train multiple ML models to learn and protect the computer's normal usage

linML uses python for data collection and model training

the project has 3 main components:

1. data collector - collects data for training and for live monitoring of the system

2. ML hub - train ML models

3. detection engine - uses ML models for detection and response

# Requirements

Linux & Python

# Quick start

1. clone the repo
2. install -r requirements.txt (use venv)
3. sudo python3 setup_collector.py --venv-path venv_name/ --module-path src.collector.learn_host
4. sudo python3 train_models.py
5. sudo python3 setup_detector.py

step 3 starts the data collector as a systemd service

step 4 trains selected models on the data collected from host

step 5 starts the detection engine as a systemd service

An in depth explanation for interacting with the data collection and detection engine services appears in the docs folder

# Methods

The following methods are currently supported:
- Endpoint binary behavior classification (iForest) - flags anomalous binaries
