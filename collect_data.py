'''
main script to collect data on host
'''
import os
import sys
import csv

import config
from src.collectors import collect_loop


default_metrics = ["timestamp", "binary", "binary_MD5_hash", "cpu", "io_read", "io_write"]

def setup_csv_file(csv_path: str = "metrics.csv",
                   metrics: list[str] | None = None) -> None:
    '''
    create a csv file in the given path with metrics as column names
    if a csv file exists, do nothing
    metrics must be from a predefined set

    Arguments:
        csv_path (str): path to create the csv file
        metrics (list[str]): list of metrics
    Raises:
        ValueError: if any metric is not from the predefined set
        FilePermissionError: no write permission to create the csv file
        FileNotFoundError: if the parent directory doesn't exist
    '''

    if metrics is None:
        metrics = default_metrics
    else:
        if not all(m in default_metrics for m in metrics):
            raise ValueError(f"Invalid metrics. Allowed: {default_metrics}")
    try:
        if not os.path.exists(csv_path):
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(metrics)

    except PermissionError as e:
        raise PermissionError(f"no write permission to create csv: {e}") from e
    except FileNotFoundError as e:
        raise FileNotFoundError(f"parent directory of {csv_path} doesn't exist: {e}") from e

def main():
    '''
    entry point for the telemetry agent
    collect data on host and dump it to a csv file
    configuration of the telemetry agent is in agent_config.py
    '''
    print("Setting up telemetry agent")
    print(f"Creating csv file in {config.CSV_PATH}")
    print(f"Emitting features every {config.EMIT_EVERY} seconds")

    setup_csv_file(csv_path = config.CSV_PATH, metrics = default_metrics)
    collect_loop(config.CSV_PATH, config.EMIT_EVERY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser shut down. Stopping Collector...\n")
    except (PermissionError, FileNotFoundError) as e:
        print(f"fatal error: {e}", file=sys.stderr)
        sys.exit(1)
