#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import math
import os
import time
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel

from core.dsbd_residue import compute_residue_v1
from core.pqc_dilithium import keygen, sign
from rb_ledger import Ledger
from rb_regua import admissible_hidden, hidden_residual


def _canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def merkle_root_hex(items: List[str]) -> str:
    layer = [bytes.fromhex(sha256_hex(x)) for x in items] or [b"\x00" * 32]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else layer[i]
            nxt.append(hashlib.sha256(a + b).digest())
        layer = nxt
    return layer[0].hex()


class Claim(BaseModel):
    claim_id: str
    claim_type: str
    subject: str
    predicate: str
    evidence: Dict[str, Any]
    organism_id: str
    observer_op: str
    state_space: str
    timestamp: float
    signature: str


class GateRequest(BaseModel):
    protocol: str = "RB-OME-1"
    organism_id: str
    observer_op: str
    state_space: str
    claims: List[Claim]


class GateResponse(BaseModel):
    evidence_id: str
    verdict: str
    omega: float
    pose: Dict[str, Any]


app = FastAPI(title="RB-Ω Gate", version="1.0.1")
ledger = Ledger("rb_ledger.sqlite3")
PQC_PK = os.environ.get("PQC_DILITHIUM_PK")
PQC_SK = os.environ.get("PQC_DILITHIUM_SK")
if not PQC_PK or not PQC_SK:
    # Gera par efêmero se não for fornecido; em produção, injete via secrets.
    PQC_PK, PQC_SK = keygen()


def omega_score(features: Dict[str, float], weights: Dict[str, float]) -> float:
    score = 0.0
    for key, weight in weights.items():
        score += float(weight) * float(features.get(key, 0.0))
    return max(0.0, min(1.0, score))


@app.post("/analyze", response_model=GateResponse)
def analyze(req: GateRequest):
    t0 = time.perf_counter()
    evidence_id = f"OME1-{uuid.uuid4().hex[:12]}"

    last = req.claims[-1].evidence if req.claims else {}
    psi = float(last.get("psi", 0.90))
    theta_p95_ms = float(last.get("theta_p95_ms", 60.0))
    cvar = float(last.get("cvar_0_95", 0.03))
    pole = float(last.get("pole", 0.90))

    theta_hat = float(math.exp(-0.01 * theta_p95_ms))
    one_minus_cvar = float(1.0 - cvar)

    residual = float(last.get("hidden_residual", abs(1.0 - psi) + cvar))
    m_hidden = hidden_residual(residual, req.organism_id)
    ok_hidden, hidden_check = admissible_hidden(m_hidden)
    residue = compute_residue_v1(
        symmetry_delta=residual,
        entropy_increase=abs(1.0 - psi),
        energy_barrier=cvar,
    )

    features = {
        "psi": psi,
        "theta_hat": theta_hat,
        "one_minus_cvar": one_minus_cvar,
        "pole": pole,
        "hidden_residual": residual,
    }
    weights = {"psi": 0.4, "theta_hat": 0.3, "one_minus_cvar": 0.2, "pole": 0.1}
    omega = omega_score(features, weights)

    checks = [
        {"rule": "psi>=0.85", "ok": psi >= 0.85, "value": psi},
        {
            "rule": "theta_p95<=100ms",
            "ok": theta_p95_ms <= 100.0,
            "value": theta_p95_ms,
        },
        {"rule": "cvar<=0.05", "ok": cvar <= 0.05, "value": cvar},
        {"rule": "omega>=0.85", "ok": omega >= 0.85, "value": omega},
        {"rule": "hidden_residual<=envelope", **hidden_check},
    ]
    hard_ok = all(bool(x["ok"]) for x in checks)
    verdict = "ADMIT" if hard_ok else ("QUARANTINE" if omega >= 0.70 else "BLOCK")

    claim_hashes = [sha256_hex(_canon(c.model_dump())) for c in req.claims]
    mr = merkle_root_hex(
        claim_hashes + [sha256_hex(_canon(features)), sha256_hex(_canon(checks))]
    )

    pose = {
        "protocol": req.protocol,
        "evidence_id": evidence_id,
        "timestamp": time.time(),
        "organism_id": req.organism_id,
        "observer_op": req.observer_op,
        "state_space": req.state_space,
        "claims": [c.model_dump() for c in req.claims],
        "governance": {
            "features": {
                "psi.v1": {"value": psi},
                "theta.v1": {"p95_ms": theta_p95_ms, "theta_hat": theta_hat},
                "cvar.v1": {
                    "alpha": 0.95,
                    "value": cvar,
                    "one_minus": one_minus_cvar,
                },
                "pole.v1": {"value": pole},
                "hidden_residual.v1": {
                    "value": residual,
                    "envelope_max": hidden_check["max"],
                },
            },
            "omega": omega,
            "verdict": verdict,
            "admissibility": {"ruleset": "RB-Ω Constitution v1.0", "checks": checks},
        },
        "proof_chain": {
            "merkle_root": mr,
            "sha256": sha256_hex(
                _canon({"claims": claim_hashes, "features": features, "checks": checks})
            ),
            "signature": {"scheme": "SIM-DILITHIUM3", "sig": sha256_hex(mr + "|sig")},
        },
        "telemetry": {"latency_ms": (time.perf_counter() - t0) * 1000.0},
    }

    # Assinatura PQC sobre payload canônico sem signatures
    pose_payload = {k: v for k, v in pose.items() if k != "proof_chain"}
    pose_payload["residue"] = residue.to_dict()

    sig_payload = dict(pose_payload)
    sig_b64 = sign(sig_payload, PQC_SK)
    pqc_signature = {"alg": "Dilithium3", "pk": PQC_PK, "sig": sig_b64}

    pose_payload["signatures"] = {"pqc": pqc_signature}
    pose_payload["proof_chain"] = pose["proof_chain"]

    # Persistência
    ledger.append(
        "GATE_DECISION",
        {"evidence_id": evidence_id, "verdict": verdict, "omega": omega},
    )
    ledger.put_evidence_append_only(evidence_id, pose_payload)

    # ledger_head é sha256 do arquivo do ledger após persistir (não assinado)
    with open(ledger.path, "rb") as handle:
        ledger_head = sha256_hex(handle.read())
    pose_payload["ledger_head"] = ledger_head

    return GateResponse(
        evidence_id=evidence_id,
        verdict=verdict,
        omega=omega,
        pose=pose_payload,
    )
