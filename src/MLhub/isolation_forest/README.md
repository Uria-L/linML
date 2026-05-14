# isolation forest

this directory contains code related to the isolation forest method

the files are as follows:

- train_isolation_forest.py: train a isolation forest models based on data collected from host, and save the models for future usage
- incident_store.py: interface for the incidents DB
- detection_engine.py: detect events on the system with the trained models
- response_engine.py: response engine based on events from the database
- paper/isolation_forest.pdf: the original paper describing the model

the directories are as follows:
- models/: directory with trained models for each binary

# Usage

to train the models run the following command:
python3 train_baseline_models.py

to detect events on the system run the following command:
python3 detection_engine.py

to respond to events run the following command:
python3 response_engine.py

# How does the module work?

There are three basic steps to use the iForest module for protecting our endpoint:
1. train the iForest models (one model per binary)
2. run the detection engine: monitor the system (collect events & send to database)
3. run the responding engine: handle incidents by querying the database (read events & respond)

# Things to do

- [] start writing the response engine
- [] write safe hash logic for flagged binaries
