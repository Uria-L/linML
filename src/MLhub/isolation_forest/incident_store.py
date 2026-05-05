'''
incident_store.py
handles DB of incidents, for the iForest method
'''

import sqlite3
import os
from src.collector.collectors import ProcState

class IncidentDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
             CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY,
                binary_path TEXT,
                flag_status TEXT,
                flag_reason TEXT,
                flag_confidence REAL,
                detected at TIMESTAMP,
                last_seen TIMESTAMP,
                count INTEGER DEFAULT 1,
                detection_metadata TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_incident(self, binary_path: str, state: ProcState) -> bool:
        '''
        log or update an incident in the database

        if an identical incident exists within the dedup window, increment count
        Otherwise, insert a new incident

        Arguments:
            binary_path (str): path to binary
            state (ProcState): current state with flagged status

        Returns:
            bool: True if new incident logged, False if deduplicated
        '''
