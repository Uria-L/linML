'''
detection_engine.py
this script runs the isolation forest detection engine
default memory method is joblib
'''
import time
import logging
from pathlib import Path
from typing import Any
from collections import defaultdict


import joblib
import onnxruntime as ort # used for onnx memory method

from src.collectors import collect, aggregate, update_state
from src.collectors import ProcState, RATE_METRICS

# step 1: load trained models

def _load_single_model(binary_dir: Path,
                      model_type: str,
                      method: str) -> Any:
    '''
    helper to handle the specific loading logic based on method

    Arguments:
        binary_dir (Path): path to directory of a binary, containing the models
        model_type (str): describes model type (baseline, or updating)
        method (str): joblib or onnx

    Returns:
        Any: model object on given binary, None if dir doesn't exists

    Raises:
        ValueError: unknown memory method
    '''
    ext = ".pkl" if method == "joblib" else ".onnx"
    target_path = binary_dir / f"{model_type}{ext}"

    if not target_path.exists():
        return None

    if method == "joblib":
        return joblib.load(target_path, mmap_mode='r')

    if method == "onnx":
        return ort.InferenceSession(str(target_path))

    raise ValueError(f"Unknown memory_method: {method}")

def load_models(path_to_models: Path = "",
                memory_method: str = "joblib") -> dict[str, tuple[Any, Any]]:
    '''
    load the isolation forest models into memory

    Arguments
        path_to_models (Path): path to dir containing iForest models
        memory_method (str): how to load models into memory

    Returns:
        dict[str, tuple[Any, Any]]: key: binary path. value: (baseline model, updating model)

    Raises:
        FileNotFoundError: path to models not found
    '''

    if not path_to_models.exists():
        raise FileNotFoundError(f"Model directory not found: {path_to_models}")

    models_registry = {}

    for binary_dir in path_to_models.iterdir():
        if not binary_dir.is_dir():
            continue

        binary_name = binary_dir.name

        baseline = _load_single_model(binary_dir, "baseline", memory_method)
        updating = _load_single_model(binary_dir, "updating", memory_method)

        if baseline or updating:
            models_registry[binary_name] = (baseline, updating)


    return models_registry

# step 2: collect features per binary

def collect_binaries_states(binaries_states: dict[str, ProcState],
                            metrics_to_collect: list[str],
                            loop_ts: int) -> int:
    '''
    update each binary's current state

    Arguments:
        binaries_states (dict[str, ProcState]): key: binary path. Value: binary's state
        metrics_to_collect (list[str]): metrics to collect on each binary
        loop_ts (int): timestamp of current collect loop

    Returns:
        int: number of states successfully updated
    '''
    pid_binary = {}
    pids_metrics = {}
    binaries_metrics = {}

    n_collected = collect(pid_binary, pids_metrics, metrics_to_collect)
    n_aggregated = aggregate(pid_binary, pids_metrics, binaries_metrics)
    n_updated = update_state(binaries_metrics, binaries_states, loop_ts)

    logging.info("collected:%d aggregated:%d updated:%d", n_collected,n_aggregated,n_updated)
    return n_updated

# step 3: predict using both baseline and updated models, per binary

def predict_per_binary(registry: dict[str, tuple(Any, Any)],
                       binaries_states: dict[str, ProcState]) -> int:
    '''
    predicts the anomaly score for each binary, using models in the registry
    updates the baseline_score and updating_score for each binary
    predicts only binaries with a model in the registry

    Arguments:
        registry (dict[str, tuple(Any, Any)]): binary path, (base model, updating model)
        binaries_states (dict[str, ProcState]): binary path, ProcState

    Returns:
        int: number of anomaly scores updated
    '''
    registered_binaries = set(registry) & set(binaries_states)

    for binary in registered_binaries:
        state = binaries_states[binary]

        baseline_model = registry[binary][0]
        updating_model = registry[binary][1]

        state.baseline_score = predict.baseline_model(state)

# step 4: flag anomalies

# step 5: output results



def isolation_forest_detection_engine():
    '''
    engine to detect and respond based on trained iForest models
    '''

    # set up data structures
    registry = load_models(Path("./models"), memory_method = "joblib")
    metrics_to_collect = RATE_METRICS
    binaries_states = defaultdict(ProcState)

    while True:
        loop_ts = time.time()

        n_states = collect_binaries_states(binaries_states, metrics_to_collect, loop_ts)


def main():
    '''entry point'''
    isolation_forest_detection_engine()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser shut down. Stopping iForest detection engine...\n")
