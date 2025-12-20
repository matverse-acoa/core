"""Aplicativo FastAPI (stub mínimo implementando endpoints da especificação)."""

from __future__ import annotations

import time
from typing import Any, Dict

from fastapi import FastAPI

app = FastAPI(title="API de Governança ACOA", version="1.0.0-beta")


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "version": "1.0.0-beta",
        "timestamp": time.time(),
    }


@app.post("/acoa/audit")
async def audit(request: Dict[str, Any]) -> Dict[str, Any]:
    _ = request
    start = time.time()
    duration = time.time() - start
    return {
        "decision": "ACCEPT",
        "invariants": {
            "psi": 0.9,
            "omega": 1.1,
            "cvar": 0.2,
            "ccr": 1.2,
            "viability": 0.9,
        },
        "proof": None,
        "metadata": {"duration_seconds": duration},
    }
