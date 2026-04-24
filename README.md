# linML

linML aims to be the simplest way to use ML to protect a linux machine

it does so by collecting data, and train multiple ML models to learn and protect the computer's normal usage

linML uses python for data collection and model training

the project has 3 main components:

1. data collector - collects data for training and for live monitoring of the system

2. ML hub - train ML models

3. detection engine - uses ML models for detection and response

# Requirements

a linux machine

python 3.12.3

# Quick start

1. clone the repo
2. pip install -r requirements.txt (it's recommended to use a virtual env)
3.

using linML has 3 steps:

1. run the data collector to collect data on your machine for X days
2. train the ML models you want
3. run the detection engine with the trained models to monitor your system

# Methods

The following methods are currently supported:
- Endpoint process behavior classification (Isolation Forest) - flags anomalous processes
