'''
collectors.py
'''
import time
import os
import hashlib
import csv
import logging
from collections import defaultdict

from .metrics import RateMetric


# logger set up
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

# Metrics to collect appear here as a single source of truth
RATE_METRICS = ["cpu", "io_read", "io_write"]

class ProcState:
    '''
    ProcState holds current state of a process.
    A process's state is made from different metrics which describe it's behavior
    '''
    def __init__(self, window_seconds=60):

        self.rates = {m: RateMetric(window_seconds) for m in RATE_METRICS}
        # self.samples = {m: SampleMetric(window_seconds) for m in samples_metrics}
        # self.count = {m: 0 for m in count_metrics}
        # self.static = {}
        self.last_updated = time.time()
        self.baseline_score = 0.0
        self.updating_score = 0.0

# Collect loop function

## Collect metrics functions


def get_binary(pid: int) -> str:
    '''
    get binary path for given PID

    Arguments: pid (int): process ID number

    Returns:
        str: path to binary

    Raises:
        FileNotFoundError: Process does not exist
        PermissionError: Insufficient permissions to read
    '''
    try:
        return os.readlink(f"/proc/{pid}/exe")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Process {pid} not found") from e
    except PermissionError as e:
        raise PermissionError(f"cannot read executable from process {pid}: {e}") from e

def metric_collect_cpu(pid: int) -> int:
    '''
    collect total cpu ticks for a given pid

    Arguments:
        pid (int): number of process ID

    Returns:
        number of ticks

    Raises:
        FileNotFoundError: process does not exist
        PermissionError: can't access process's stats
        ValueError: can't parse stat file
    '''
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as f:
            data = f.read().split()

        utime = int(data[13])
        stime = int(data[14])

        return utime + stime

    except FileNotFoundError as e:
        raise FileNotFoundError(f"process {pid} not found") from e
    except PermissionError as e:
        raise PermissionError(f"can't read {pid} stats") from e
    except (ValueError, IndexError) as e:
        raise ValueError(f"can't parse stat file for process {pid}: {e}") from e

def metric_collect_io_read(pid: int) -> int:
    '''
    collects total bytes read for a given pid

    Arguments:
        pid (int): number of process id to collect data

    Returns:
        number of bytes read on success

    Raises:
        FileNotFoundError: process doesn't exist
        PermissionError: can't access io file
        ValueError: can't parse io file

    '''
    try:
        with open(f"/proc/{pid}/io", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("rchar:"):
                    return int(line.split()[1])

        raise ValueError(f"rchar line not found in io file for process {pid}")

    except (FileNotFoundError, ProcessLookupError) as e:
        raise FileNotFoundError(f"can't find process {pid} io file") from e
    except PermissionError as e:
        raise PermissionError(f"can't access process {pid} io file") from e
    except (IndexError, ValueError) as e:
        raise ValueError(f"can't parse io file for process {pid}: {e}") from e

def metric_collect_io_write(pid: int) -> int:
    '''
    collects total bytes wrote for a given pid

    Arguments:
        pid (int): number of process id to collect data on

    Returns:
        number of bytes wrote on success

    Raises:
        FileNotFoundError: process doesn't exist
        PermissionError: can't access io file
        ValueError: can't parse io file

    '''
    try:
        with open(f"/proc/{pid}/io", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("wchar:"):
                    return int(line.split()[1])

        raise ValueError(f"wchar line not found in io file for process {pid}")

    except (FileNotFoundError, ProcessLookupError) as e:
        raise FileNotFoundError(f"can't find process {pid} io file") from e
    except PermissionError as e:
        raise PermissionError(f"can't access process {pid} io file") from e
    except (IndexError, ValueError) as e:
        raise ValueError(f"can't parse io file for process{pid}: {e}") from e


# All collectors must accept (pid: int) and raise only:
# - FileNotFoundError: process doesn't exist
# - PermissionError: can't access process data
# - ValueError: data parsing failed
METRIC_COLLECTORS = {
    "cpu": metric_collect_cpu,
    "io_read": metric_collect_io_read,
    "io_write": metric_collect_io_write
}

def collect_metric(pid:int, metric: str) -> int:
    '''
    collect metrics on for a given pid

    Argument:
        pid (int): pid number to collect data on
        metric (str): type of metric to be collected

    Returns:
        value of the metric collected

    Raises:
        ValueError: metric requested doesn't exist
    '''
    if metric not in METRIC_COLLECTORS:
        raise ValueError(f"Unknown metric: {metric}")

    return METRIC_COLLECTORS[metric](pid)

def collect_per_pid(pid: int, metrics: list[str]) -> dict[str, int]:
    '''
    collect metrics about pid, return as a dict
    if failed to collect any metric, log the event and continue

    Arguments:
        pid (int): pid number to collect data
        metrics (list[str]): metrics to be collected

    Returns:
        dict[str, int]: dictionary containing successfully collected metrics
    '''

    pid_metrics = {}

    for metric in metrics:
        try:
            metric_val = collect_metric(pid, metric)
            pid_metrics[metric] = metric_val

        except (FileNotFoundError, ProcessLookupError, PermissionError) as e:
            logging.debug("can't collect %s for %d: %s", metric, pid, e)
            continue
        except ValueError as e:
            logging.warning("parse error for %s on %d: %s", metric, pid, e)
            continue

    return pid_metrics

def collect(pid_binary: dict[int, str],
            pids_metrics: dict[int, dict[str, int]],
            metrics_to_collect: list) -> int:
    '''
    collect telemetry on each pid

    Arguments:
        pid_binary (dict[int, str]): pid -> binary
        pids_metrics (dict[int, dict[str, int]]): pid -> (metric, value)
        metrics_to_collect (list): metrics to collect for each pid

    Returns:
        number of times data was collected on a pid successfully
    '''
    n_collected = 0
    for pid_str in os.listdir("/proc"):
        if not pid_str.isdigit():
            continue

        pid = int(pid_str)
        try:
            binary = get_binary(pid)
            metrics = collect_per_pid(pid, metrics_to_collect)
            if metrics:
                pid_binary[pid] = binary
                pids_metrics[pid] = metrics
                n_collected += 1

        except FileNotFoundError as e:
            logging.debug("couldn't find %s's binary name: %s", pid, e)
            continue
        except PermissionError as e:
            logging.debug("couldn't read %d's binary name: %s", pid, e)
            continue

    return n_collected

## Aggregate metrics functions

def update_cpu(binary_metrics: defaultdict[str, int],
               pid_cpu: int) -> None:
    ''' update binary's CPU metric '''
    binary_metrics["cpu"] = binary_metrics.get("cpu", 0) + pid_cpu

def update_io_read(binary_metrics: defaultdict[str, int],
                   pid_io_read: int) -> None:
    ''' update binary's io_read metric '''
    binary_metrics["io_read"] = binary_metrics.get("io_read", 0) + pid_io_read

def update_io_write(binary_metrics: defaultdict[str, int],
                    pid_io_write: int) -> None:
    ''' update binary's io_write metric '''
    binary_metrics["io_write"] = binary_metrics.get("io_write", 0) + pid_io_write

HANDLERS =  {
    'cpu': update_cpu,
    'io_read': update_io_read,
    'io_write': update_io_write
}

def update_binary_metrics(pid_metrics: dict[str, int],
                          binary_metrics: dict[str, int]) -> int:
    '''
    updates binary metrics in place with values from pid metrics

    Arguments:
        pid_metrics (dict[str, int]): key: name of metric. value: value of metric
        binary_metrics (dict[str, int]): key: name of metric. value: value of metric

    Returns:
        number of metrics updated.

    Raises:
        ValueError: no handler for input metric
    '''
    updated = 0
    for metric, value in pid_metrics.items():

        if value is None:
            continue

        handler = HANDLERS.get(metric)

        if handler:
            try:
                handler(binary_metrics, value)
                updated += 1
            except ValueError as e:
                raise ValueError(f"handler of {metric} failed: {e}") from e

        else:
            logging.warning("Warning: No handler for metric %s", metric)
            continue

    return updated

def aggregate(pid_binary: dict[int, str],
              pids_metrics: dict[int, dict[str, int]],
              binaries_metrics: dict[str, dict[str, int]]) -> int:
    '''
    aggregate metrics from pid to corresponding binary

    Arguments:
        pid_binary (Dict[int, str]): key: pid. value: binary name
        pids_metrics (Dict[int, Dict[str, int]]): key: pid. value: (metric, value)
        binaries_metrics (Dict[str, Dict[str, int]]): key: binary. value: (metric, value)

    Returns:
        number of pids successfully updated
    '''
    pids_updated = 0
    for pid, binary in pid_binary.items():

        pid_metrics = pids_metrics.get(pid)
        if pid_metrics is None:
            # every pid should have metrics dict, shouldn't happen
            continue

        binary_metrics = binaries_metrics.setdefault(binary, {})
        n_updated = update_binary_metrics(pid_metrics, binary_metrics)
        if n_updated > 0:
            pids_updated += 1


    return pids_updated

# update state functions
def update_state(
        binaries_metrics: dict[str, dict[str, int]],
        states: dict[str, ProcState],
        loop_ts: int) -> int:
    '''
    updates state for each binary with the given metrics.

    Arguments:
        binaries_metrics(dict[str, dict[str, int]]): ( binary, ( metric, value) )
        states (dict[str, ProcState]): (binary, state)
        loop_ts (int): timestamp of current collecting loop

    Returns:
        number of states updated.
    '''
    n_updated = 0

    for binary, metrics_dict in binaries_metrics.items():
        state = states[binary]

        for metric_name, value in metrics_dict.items():
            if metric_name in state.rates:
                state.rates[metric_name].update(value, loop_ts)
                state.last_updated = loop_ts
                n_updated += 1

    return n_updated

# prune stale binaries
def prune_binaries(binaries_states: dict[str, ProcState], loop_ts: int, stale_timeout: int):
    '''
    prunes binaries which aren't active

    Arguments:
        binaries_state (dict[str, ProcState]): key: binary path, value: ProcState
        loop_ts (int): current collect loop time
        stale_timeout (int): the time in seconds after which a binary is removed

    Returns:
        number of binaries pruned

    '''
    n_pruned = 0
    stale_binaries = [
        binary for binary, state in binaries_states.items()
        if loop_ts - state.last_updated > stale_timeout
    ]
    for binary in stale_binaries:
        del binaries_states[binary]
        n_pruned += 1
        logging.info("removed stale binary: %s", binary)

    return n_pruned

# Emit features functions
def emit_features(csv_path: str, binaries_states: defaultdict[str, ProcState]) -> int:
    '''
    emits the content of a states dictionary to a csv file

    Arguments:
        csv_path (str): path to csv file
        binaries_states(defaultdict[str, ProcState]): key: binary path. value: ProcState

    Returns:
        int: the number of rows written to FILE

    Raises:
        IOError: if the file cannot be opened or written to
        Exception: if any other error occurs during writing
    '''
    ts = time.time()

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for binary, state in binaries_states.items():
            writer.writerow([
                ts,
                binary,
                hashlib.md5(binary.encode("utf-8")).hexdigest(),
                state.rates["cpu"].mean(),
                state.rates["io_read"].mean(),
                state.rates["io_write"].mean()
            ])
    rows_written = len(binaries_states)
    return rows_written

def collect_loop(csv_path: str, emit_every: int):
    '''
    main collect loop on host.
    emit each binary's state to a csv file, every emit_every seconds

    Arguments:
        csv_path (str): path to csv file which holds the data
        emit_every (int): how many seconds between each emit

    '''

    logging.info("started collecting data on host. to exit, press CTRL-C")
    logging.info("csv_path: %s, emit_every: %s", csv_path, emit_every)

    metrics_to_collect = RATE_METRICS
    binaries_states = defaultdict(ProcState)

    last_emit = time.time()
    while True:
        loop_ts = time.time()

        # 1. Collect per PID:
        pid_binary = {}
        pids_metrics = {}
        binaries_metrics = {}

        n_collected = collect(pid_binary, pids_metrics, metrics_to_collect)

        # 2. aggregate per binary
        n_aggregated = aggregate(pid_binary, pids_metrics, binaries_metrics)

        # 3. update state
        n_updated = update_state(binaries_metrics, binaries_states, loop_ts)

        # 4. prune stale binaries
        n_pruned = prune_binaries(binaries_states, loop_ts, stale_timeout = 60)

        logging.info("collected: %d aggregated: %d",n_collected,n_aggregated)
        logging.info("updated %d states", n_updated - n_pruned)


        # 4. emit features
        if time.time() - last_emit > emit_every:
            try:
                nfeatures = emit_features(csv_path, binaries_states)
                last_emit = time.time()
                logging.info("emitted %d features at time %d", nfeatures, last_emit)
            except (IOError, OSError) as e:
                logging.warning("disk IO failed: %s", e)

        time.sleep(5)
