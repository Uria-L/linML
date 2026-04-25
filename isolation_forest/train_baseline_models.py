'''
train_baseline_models.py
train baseline and updating isolation forest models, for each binary
each model is saved in a separate directory
'''

from datetime import datetime
from pathlib import Path
import json
import sys

import joblib
from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np


# CSV path setup
SCRIPT_DIR = Path(__file__).parent.absolute()
# PATH_TO_CSV = SCRIPT_DIR.parent / "data" / "metrics.csv"
PATH_TO_CSV = ""
# model training functions

def _sanitize_binary_name(binary_path) -> str:
    '''Convert binary file path to a safe directory name'''
    return str(binary_path).replace("/", "_")

def _train_model(x_mat: np.ndarray,
                 contamination: float=0.01,
                 random_state: int=1984) -> IsolationForest:
    """
    Train a single Isolation Forest model

    Arguments:
    x_mat (pd.DataFrame): matrix with numeric features
    contamination (int): proportion of outliers in the data set
    random_state (int): controls psuedo-randomness

    Returns:
        model (IsolationForest): object with trained model
    """
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1
    )
    model.fit(x_mat)
    return model

def _save_models(binary: str,
                 baseline: IsolationForest,
                 updating: IsolationForest,
                 model_dir: Path) -> None:
    """
    dumps the baseline and updating models for a given binary

    Arguments:
        binary (str): name of binary
        baseline (IsolationForest): baseline model object
        updating (IsolationForest): updating model object
        model_dir (str): path to the models directory
    """
    safe_binary_name = _sanitize_binary_name(binary)
    binary_dir = model_dir / safe_binary_name
    binary_dir.mkdir(exist_ok=True)

    joblib.dump(baseline, binary_dir / "baseline.joblib")
    joblib.dump(updating, binary_dir / "updating.joblib")

def _generate_metadata(binary: str,
                       x_mat: np.ndarray,
                       contamination: float) -> dict[str, dict]:
    """
    Generate metadata for a binary
    Arguments:
        binary (str): name of binary
        x_mat (np.ndarray): numpy matrix used for training the iForest model
        contamination (float): proportions of outliers in the dataset

    Returns:
        dict[str, dict]: binary, metadata
    """
    safe_binary_name = _sanitize_binary_name(binary)
    return {
        safe_binary_name: {
            "trained_date": datetime.now().isoformat(),
            "n_samples": len(x_mat),
            "n_features": x_mat.shape[1],
            "baseline_threshold": 0.6,
            "updating_threshold": 0.65,
            "contamination": contamination,
            "window_size": 1000,
            "retrain_interval_hours": 6
        }
    }

def _save_metadata(results: dict[str, dict],
                   model_dir: Path) -> None:
    """
    Save metadata to JSON file
    Arguments:
        results (dict[str, dict]): key: binary. value: meta-data
        model_dir (Path): path to the models directory
    """
    flattened = {}
    for meta in results.values():
        flattened.update(meta)

    with open(model_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(flattened, f, indent=2)

def train_model_by_binary(df: pd.DataFrame,
                     model_dir="models",
                     contamination=0.01,
                     random_state=1984,
                     binary_column="binary") -> dict[str, dict]:
    """
    Train baseline and initial updating models for each binary.

    Args:
        df: DataFrame with numeric features and a 'binary' column
        model_dir: directory to save models
        contamination: contamination parameter for IsolationForest
        random_state: random state for reproducibility
        binary_column: name of a column with binaries paths

    Returns:
        Dictionary with metadata for each binary
    """
    model_dir = Path(model_dir)
    model_dir.mkdir(exist_ok=True)

    results = {}
    features_to_drop = [binary_column]

    for binary, binary_df in df.groupby(binary_column):
        print(f"\nTraining models for: {binary}")

        # Split dataframe by binary
        x_mat = binary_df.drop(columns=features_to_drop).values

        # Train both models on the same data
        baseline = _train_model(x_mat, contamination, random_state)
        updating = _train_model(x_mat, contamination, random_state)

        # Save
        _save_models(binary, baseline, updating, model_dir)
        results[binary] = _generate_metadata(binary, x_mat, contamination)

        print(f"  ✓ Trained on {len(x_mat):,} samples, {x_mat.shape[1]} features")

    _save_metadata(results, model_dir)
    return results

# data functions
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

def clean_data(df: pd.DataFrame,
               timestamp_col: str = "timestamp",
               keep_binary: str = "binary") -> pd.DataFrame:
    '''
    returns a cleaned dataframe for the isolation forest model
    - drops the timestamp column (if present)
    - keeps only numeric columns plus the 'binary' column (if present)

    Arguments:
        df (pd.DataFrame):   dataframe with the entire data
        timestamp_col (str): timestamp column to remove
        keep_binary (str):   binary column to keep

    Returns:
        pd.DataFrame: clean data for training
    '''
    df = df.copy()

    # drop timestamp column
    if timestamp_col in df.columns:
        df = df.drop(columns=[timestamp_col])

    # keep numeric columns and the binary column
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cols_to_keep = set(numeric_cols)
    if keep_binary in df.columns:
        cols_to_keep.add(keep_binary)

    return df.loc[:, [c for c in df.columns if c in cols_to_keep]]

# wrapper for the training process
def train_models(path_to_csv: str) -> dict[str, dict]:
    '''
    train iForest models for each binary

    Arguments:
        path_to_csv (str): path to data in CSV format

    Returns:
        results (dict[str, dict]): key: binary. value: meta-data
    '''
    df = load_data(path_to_csv)
    clean_df = clean_data(df)
    results = train_model_by_binary(clean_df)

    return results

def main():
    '''
    main entry point
    '''
    results = train_models(PATH_TO_CSV)
    n_models = len(results)
    print(f"successfully trained {n_models} models. ")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"fatal error: {e}")
        sys.exit(1)
