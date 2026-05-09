'''
incident_store.py
handles DB of incidents, for the iForest method
'''

import sqlite3
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DetectionEvent:
    '''
    detection event data structure.
    '''
    binary_path: str
    anomaly_score: float
    detected_at: datetime

class IncidentDB:
    '''
    manages the incidentDB with the following methods:
    init_db: initiate the DB
    ingest: read events from the detection engine, write to DB
    '''
    INCIDENT_FIELDS = {
        "binary_path": "TEXT",
        "anomaly_score": "FLOAT",
        "detected_at": "TIMESTAMP"
    }
    TYPE_MAP = {"TEXT": str, "FLOAT": float, "TIMESTAMP": datetime}

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        '''
        initate the incidents DB in db_path
        '''

        conn = sqlite3.connect(self.db_path)
        cols = ", ".join(f"{field} {dtype}" for field, dtype in self.INCIDENT_FIELDS.items())
        query = f"""
                 CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY,
                    {cols}
                 )
                """
        conn.execute(query)
        conn.commit()
        conn.close()

    def _validate_event(self, event: DetectionEvent) -> None:
        '''
        validate each event field, with the Class's INCIDENT_FIELDS

        Arguments:
            event (DetectionEvent): event instance

        Raises:
            ValueError: a field in event is missing
            TypeError: wrong data type for some field
        '''

        for field, dtype in self.INCIDENT_FIELDS.items():
            value = getattr(event, field, None)
            if value is None:
                raise ValueError(f"Missing field: {field}")
            expected_type = self.TYPE_MAP[dtype]
            if not isinstance(value, expected_type):
                raise TypeError(f"field {field} expects {dtype}, got {type(value).__name__}")

    def filter_valid_events(self, events: list[DetectionEvent]) -> tuple[list[DetectionEvent], int]:
        '''
        filters list of events, making sure valid fields and values

        Arguments:
            events (list[DetectionEvent]): list of events to filter

        Returns:
            tuple[list[DetectionEvent], int]: (list of valid events, count of bad events)
        '''
        valid_events = []
        error_count = 0

        for event in events:
            try:
                self._validate_event(event)
                valid_events.append(event)
            except (ValueError, TypeError) as e:
                print(f"validation failed for {event.binary_path}: {e}")
                error_count += 1

        return valid_events, error_count

    def _commit_batch(self, conn: sqlite3.Connection, batch: list[DetectionEvent]) -> None:
        '''
        specialized sub-transaction worker

        Arguments:
            conn (sqlite3.Connection): open sqlite connection to a DB
            batch (list[DetectionEvent]): list of events to send
        '''
        cols = ", ".join(self.INCIDENT_FIELDS.keys())
        placeholders = ", ".join(["?"] * len(self.INCIDENT_FIELDS))
        query = f"INSERT INTO incidents ({cols}) VALUES ({placeholders})"

        try:
            with conn:
                data = [
                    tuple(getattr(event, field) for field in self.INCIDENT_FIELDS)
                    for event in batch
                ]

                conn.executemany(query, data)
        except sqlite3.Error as e:
            print(f"Database batch insertion failed: {e}")

    def ingest(self, events: list[DetectionEvent], batch_size: int = 100) -> None:
        '''
        ingest events from detection engine
        '''

        valid_events, n_errors = self.filter_valid_events(events)

        if not valid_events:
            print(f"ingestion stopped: 0 valid events found ({n_errors} errors)")

        conn = sqlite3.connect(self.db_path)
        try:
            for i in range(0, len(valid_events), batch_size):
                batch = valid_events[i: i + batch_size]
                self._commit_batch(conn, batch)
        finally:
            conn.close()

        print(f"Ingestion complete: {len(valid_events)} success, {n_errors} errors.")
