'''
incident_store.py
handles DB of incidents, for the iForest method
'''

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

from src.collector.collectors import ProcState

@dataclass
class DetectionEvent:
    '''
    detection event data structure. used by detection engine.
    '''
    binary_path: str
    anomaly_score: float
    detected_at: datetime
    parent: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

class IncidentDB:
    '''
    manages the incidentDB with the following methods:
    init_db: initiate the DB
    ingest: read events from the detection engine, write to DB
    '''
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        '''
        initate the incidents DB in db_path
        '''
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
             CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY,
                binary_path TEXT,
                detected_at TIMESTAMP,
                last_seen TIMESTAMP,
                count INTEGER DEFAULT 1,
                metadata TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def ingest(self, events: list[DetectionEvent]) -> None:
        '''
        ingest events from detection engine
        '''
