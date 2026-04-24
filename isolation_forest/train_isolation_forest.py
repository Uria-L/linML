'''
train_isolation_forest.py
this script trains an isolation forest model with data collected on given host
the model is saved as an object on the directory this script was executed on
'''

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

# CSV path setup
SCRIPT_DIR = Path(__file__).parent.absolute()
PATH_TO_CSV = SCRIPT_DIR.parent / "data" / "metrics.csv"

def load_data(path_to_csv: str) -> pd.DataFrame:
    '''
    load CSV as a pandas dataframe

    Arguments:
        path_to_csv(str): path to csv file containing data on host

    Returns:
        pd.DataFrame with data. raise appropriate error if failed
    '''
    try:
        return pd.read_csv(path_to_csv)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Data not found in {path_to_csv}") from e
    except pd.errors.ParserError as e:
        raise ValueError(f"corrupt CSV file: {e}") from e

def extract_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    '''
    extract numeric features only for isolation forest
    '''

    # only numeric features
    numeric_features = df.select_dtypes(include=['number'])

    # remove timestamp from training data
    numeric_features = numeric_features.drop(columns=['timestamp'], errors='ignore')
    if numeric_features.empty:
        raise ValueError("No numeric features found")
    return numeric_features


def isolation_forest_train(path_to_csv: str) -> IsolationForest:
    '''
    train an isolation forest model from data in a CSV file

    Arguments:
        path_to_csv(str): path to the csv file containing the data

    Returns:
        IsolationForest (object): fitted isolation forest model
    '''

    df = load_data(path_to_csv)
    numeric_features = extract_numeric_features(df)

    print(f"starting to train an isolation forest model with {len(df)} rows...")
    isolation_forest_model = IsolationForest(random_state = 1984)
    isolation_forest_model.fit(numeric_features)
    return isolation_forest_model

if __name__ == "__main__":
    try:
        model = isolation_forest_train(PATH_TO_CSV)
        print("Training successful. dumping model as isolation_forest.pkl in current directory")
        joblib.dump(model, "isolation_forest.pkl")
    except FileNotFoundError as e:
        print(f"Setup failed: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Data invalid: {e}")
        sys.exit(1)
