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
3. sudo python3 setup.py

when you run setup.py, 3 tasks are scheduled:

1. run the data collector to collect data on your machine for X days
2. train the ML models you want
3. run the detection engine with the trained models to monitor your system

# Methods

The following methods are currently supported:
- Endpoint binary behavior classification (iForest) - flags anomalous binaries
