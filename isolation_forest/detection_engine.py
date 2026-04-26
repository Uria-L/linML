'''
detection_engine.py
this script runs the isolation forest detection engine
default memory method is joblib
'''
from pathlib import Path
from typing import Any

import joblib
import onnxruntime as ort # used for onnx memory method




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

# step 3: predict using both baseline and updated models, per binary

# step 4: flag anomalies

# step 5: output results



def isolation_forest_detection_engine():
    '''
    engine to detect and respond based on trained iForest models
    '''
    try:
        registry = load_models(Path("./models"), memory_method = "joblib")
        print(f"loaded {len(registry)} models to memory")
    except PermissionError as e:
        raise PermissionError(f"No permission to load models: {e}") from e

def main():
    '''entry point'''
    isolation_forest_detection_engine()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser shut down. Stopping iForest detection engine...\n")
