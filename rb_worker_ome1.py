#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import time
import uuid

import requests


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def make_claim(
    subject: str,
    predicate: str,
    organism_id: str,
    observer_op: str,
    state_space: str,
    evidence: dict,
):
    ts = time.time()
    claim = {
        "claim_id": f"CL-{uuid.uuid4().hex[:10]}",
        "claim_type": "metamorphosis" if "state_" in predicate else "context",
        "subject": subject,
        "predicate": predicate,
        "evidence": evidence,
        "organism_id": organism_id,
        "observer_op": observer_op,
        "state_space": state_space,
        "timestamp": ts,
    }
    claim["signature"] = sha256_hex(_canon(claim))
    return claim


def post_with_retry(url: str, payload: dict, timeout_total_s: float = 20.0):
    t0 = time.time()
    attempt = 0
    last_err = None
    while (time.time() - t0) < timeout_total_s:
        attempt += 1
        try:
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            return resp
        except Exception as exc:  # pragma: no cover - robust startup
            last_err = exc
            time.sleep(min(0.25 * attempt, 2.0))
    raise RuntimeError(f"Gate not ready after {timeout_total_s}s. Last error: {last_err}")


def main():
    gate = "http://rb_gate:8000/analyze"
    organism_id = "informacional"
    observer_op = "pose.json.v1"
    state_space = "prob-dist"
    subject = "MatVerse"

    c1 = make_claim(
        subject,
        "state_1",
        organism_id,
        observer_op,
        state_space,
        {"psi": 0.92, "theta_p95_ms": 70, "cvar_0_95": 0.03, "pole": 0.90},
    )

    c2 = make_claim(
        subject,
        "state_2",
        organism_id,
        observer_op,
        state_space,
        {
            "psi": 0.88,
            "theta_p95_ms": 85,
            "cvar_0_95": 0.04,
            "pole": 0.91,
            "hidden_residual": 0.52,
        },
    )

    payload = {
        "protocol": "RB-OME-1",
        "organism_id": organism_id,
        "observer_op": observer_op,
        "state_space": state_space,
        "claims": [c1, c2],
    }

    t0 = time.time()
    response = post_with_retry(gate, payload, timeout_total_s=20.0)
    t1 = time.time()
    out = response.json()

    receipt = {
        "ome": "OME-1",
        "timestamp": time.time(),
        "request_hash": sha256_hex(_canon(payload)),
        "response_hash": sha256_hex(_canon(out)),
        "latency_ms_client": (t1 - t0) * 1000.0,
        "evidence_id": out["evidence_id"],
        "verdict": out["verdict"],
        "omega": out["omega"],
        "pose_merkle_root": out["pose"]["proof_chain"]["merkle_root"],
        "pose_sha256": out["pose"]["proof_chain"]["sha256"],
    }
    receipt["receipt_hash"] = sha256_hex(_canon(receipt))

    with open("receipt_ome1.json", "w", encoding="utf-8") as file:
        file.write(_canon(receipt))

    print(_canon(receipt))


if __name__ == "__main__":
    main()
