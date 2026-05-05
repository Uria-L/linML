# isolation forest

this directory contains code related to the isolation forest method

the files are as follows:

- train_isolation_forest.py: train an isolation forest model based on data collected on host, and save the model for future usage
- incident_store.py: interface for the incidents DB
- detection_engine.py: monitor the system with the trained models

- paper/isolation_forest.pdf: the original paper describing the model

the directories are as follows:
- models/: directory with trained models for each binary

# Usage

to train the models run the following command:

python3 train_baseline_models.py

to monitor the system run the following command:

python3 detection_engine.py

# How does the module work?

There are two basic steps to use the iForest module for protecting our endpoint:
1. train the iForest models (one model per binary)
2. run the detection engine, which handles incidents by logging and responding
