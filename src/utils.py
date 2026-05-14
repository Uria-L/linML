'''
utils.py
'''
from pathlib import Path
from .collector.collectors import ProcState


def _desanitize_binary_name(encoded_path: str) -> Path:
    '''
    decode a path for a binary, where underscore replace slashes

    Arguments:
        encoded_path (str): the path to a binary, with underscores
    Returns:
        (Patj): path to binary with slahes
    '''
    return Path("/" + encoded_path.lstrip("_").replace("_", "/"))

def _sanitize_binary_name(binary_path: str) -> str:
    '''
    Convert binary file path to a safe directory name
    '''
    return str(binary_path).replace("/", "_")


def print_anomaly_score(binaries_states: dict[str, ProcState]) -> None:
    '''
    prints anomaly scores of every binary

    Arguments:
        binaries_states (dict[str, ProcState]): key: binary's path. value: state
    '''
    for binary, state in binaries_states.items():
        print(f"---binary:{binary}, b_score:{state.baseline_score}, u_score:{state.updating_score}")
