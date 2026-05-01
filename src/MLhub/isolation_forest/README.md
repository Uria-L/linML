# isolation forest

this directory contains code related to the isolation forest method

the files are as follows:

- train_isolation_forest.py: train an isolation forest model based on data collected on host, and save the model for future usage
- detection_engine.py: monitor the system with trained the trained models
- paper/isolation_forest.pdf: the original paper describing the model

the directories are as follows:
- models/: directory with trained models for each binary

# Usage

make sure you meet the following requirements:

1. CSV file with the following demand:
   - a column named "binary" with entries to the binary's path

2. the variable PATH_TO_CSV in train_isolation_forest.py is configured to your CSV file's location

by default, the script uses: PATH_TO_CSV = ../data/metrics.csv

to train the models run the following command:

python3 train_baseline_models.py

to monitor the system run the following command:

python3 detection_engine.py
