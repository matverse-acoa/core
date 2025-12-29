#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import numpy as np


@dataclass(frozen=True)
class Metric:
    metric_id: str
    value: float
    organism_id: str
    observer_op: str
    state_space: str
    units: str = "unitless"


def require_tags(m: Metric) -> None:
    for x in (m.metric_id, m.organism_id, m.observer_op, m.state_space):
        if not x or not isinstance(x, str):
            raise ValueError("Invalid metric tags")


def hidden_residual(error_after_best_model: float, organism_id: str) -> Metric:
    return Metric(
        metric_id="hidden_residual.v1",
        value=float(error_after_best_model),
        organism_id=organism_id,
        observer_op="regua.hidden.v1",
        state_space="residual-space",
        units="loss",
    )


def envelope_max(organism_id: str) -> float:
    table = {
        "informacional": 0.60,
        "semântico": 0.55,
        "sistêmico": 0.65,
        "físico": 0.70,
        "matemático": 0.50,
        "manifesto": 0.60,
    }
    return float(table.get(organism_id, 0.60))


def admissible_hidden(m: Metric) -> Tuple[bool, Dict[str, Any]]:
    require_tags(m)
    mx = envelope_max(m.organism_id)
    ok = m.value <= mx
    return ok, {"metric": m.metric_id, "value": m.value, "max": mx, "ok": ok}
