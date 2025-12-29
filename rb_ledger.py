#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from typing import Any, Dict, Optional, Tuple


def _canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class Ledger:
    """
    Ledger SQLite thread-safe, append-only:
    - events: cadeia de hash
    - evidence: imutável (sem overwrite)
    """

    def __init__(self, path: str = "rb_ledger.sqlite3"):
        self.path = path
        self._lock = threading.Lock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL;")
        self.db.execute("PRAGMA synchronous=NORMAL;")
        self.db.execute("PRAGMA foreign_keys=ON;")

        self.db.execute(
            """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            kind TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            prev_hash TEXT,
            this_hash TEXT NOT NULL
        );
        """
        )

        self.db.execute(
            """
        CREATE TABLE IF NOT EXISTS evidence (
            evidence_id TEXT PRIMARY KEY,
            ts REAL NOT NULL,
            pose_json TEXT NOT NULL,
            pose_hash TEXT NOT NULL
        );
        """
        )

        self.db.commit()

    def close(self) -> None:
        with self._lock:
            self.db.close()

    def _last_hash(self) -> Optional[str]:
        cur = self.db.execute("SELECT this_hash FROM events ORDER BY id DESC LIMIT 1;")
        row = cur.fetchone()
        return row[0] if row else None

    def append(self, kind: str, payload: Dict[str, Any]) -> Tuple[int, str]:
        ts = time.time()
        prev = self._last_hash()
        payload_json = _canon(payload)
        body = {"ts": ts, "kind": kind, "payload_json": payload_json, "prev_hash": prev}
        h = sha256_hex(_canon(body))

        with self._lock:
            cur = self.db.execute(
                "INSERT INTO events(ts,kind,payload_json,prev_hash,this_hash) VALUES(?,?,?,?,?)",
                (ts, kind, payload_json, prev, h),
            )
            self.db.commit()
            return int(cur.lastrowid), h

    def put_evidence_append_only(self, evidence_id: str, pose: Dict[str, Any]) -> str:
        ts = time.time()
        pose_json = _canon(pose)
        pose_hash = sha256_hex(pose_json)

        with self._lock:
            cur = self.db.execute(
                "SELECT pose_hash FROM evidence WHERE evidence_id=?", (evidence_id,)
            )
            row = cur.fetchone()
            if row:
                raise ValueError(
                    f"Evidence already exists: {evidence_id} (pose_hash={row[0]})"
                )

            self.db.execute(
                "INSERT INTO evidence(evidence_id,ts,pose_json,pose_hash) VALUES(?,?,?,?)",
                (evidence_id, ts, pose_json, pose_hash),
            )
            self.db.commit()

        self.append("EVIDENCE_STORED", {"evidence_id": evidence_id, "pose_hash": pose_hash})
        return pose_hash

    def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        cur = self.db.execute("SELECT pose_json FROM evidence WHERE evidence_id=?", (evidence_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None
