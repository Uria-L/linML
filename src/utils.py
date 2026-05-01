'''
utils.py
'''

from .collector.collectors import ProcState

def _sanitize_binary_name(binary_path) -> str:
    '''Convert binary file path to a safe directory name'''
    return str(binary_path).replace("/", "_")


def print_anomaly_score(binaries_states: dict[str, ProcState]) -> None:
    '''
    prints anomaly scores of every binary

    Arguments:
        binaries_states (dict[str, ProcState]): key: binary's path. value: state
    '''
    for binary, state in binaries_states.items():
        print(f"---binary:{binary}, b_score:{state.baseline_score}, u_score:{state.updating_score}")
