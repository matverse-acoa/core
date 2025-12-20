"""Núcleo ACOA: módulo de autopoiesis.

Implementa a medição do fechamento operacional por meio da Taxa de Fechamento
Causal (CCR).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass
class SystemState:
    internal: np.ndarray
    external: np.ndarray
    output: np.ndarray
    timestamp: float


@dataclass
class CCRMeasurement:
    ccr: float
    j_internal_norm: float
    j_external_norm: float
    timestamp: float
    is_autopoietic: bool


class AutopoieticCore:
    def __init__(
        self,
        closure_threshold: float = 1.0,
        buffer_size: int = 1000,
        epsilon: float = 1e-10,
    ) -> None:
        self.closure_threshold = closure_threshold
        self.epsilon = epsilon
        self.ccr_history: deque[CCRMeasurement] = deque(maxlen=buffer_size)
        self.state_history: deque[SystemState] = deque(maxlen=100)

    def measure_ccr(
        self,
        state_t: SystemState,
        state_t_minus_1: Optional[SystemState] = None,
        delta_t: float = 1.0,
    ) -> CCRMeasurement:
        if state_t_minus_1 is None:
            state_t_minus_1 = SystemState(
                internal=np.zeros_like(state_t.internal),
                external=np.zeros_like(state_t.external),
                output=np.zeros_like(state_t.output),
                timestamp=state_t.timestamp - delta_t,
            )
        delta_internal = state_t.internal - state_t_minus_1.internal
        delta_external = state_t.external - state_t_minus_1.external
        delta_output = state_t.output - state_t_minus_1.output

        j_internal_norm = np.linalg.norm(delta_output) / (
            np.linalg.norm(delta_internal) + self.epsilon
        )
        j_external_norm = np.linalg.norm(delta_output) / (
            np.linalg.norm(delta_external) + self.epsilon
        )
        ccr = j_internal_norm / (j_external_norm + self.epsilon)
        is_autopoietic = ccr > self.closure_threshold

        measurement = CCRMeasurement(
            ccr=ccr,
            j_internal_norm=j_internal_norm,
            j_external_norm=j_external_norm,
            timestamp=state_t.timestamp,
            is_autopoietic=is_autopoietic,
        )
        self.ccr_history.append(measurement)
        self.state_history.append(state_t)
        return measurement

    def verify_operational_autopoiesis(
        self, min_probability: float = 0.95
    ) -> Tuple[bool, float]:
        if len(self.ccr_history) == 0:
            return False, 0.0
        autopoietic_count = sum(1 for m in self.ccr_history if m.is_autopoietic)
        p_autopoietic = autopoietic_count / len(self.ccr_history)
        return (p_autopoietic >= min_probability, p_autopoietic)

    def get_statistics(self) -> dict:
        if len(self.ccr_history) == 0:
            return {
                "mean_ccr": 0.0,
                "std_ccr": 0.0,
                "min_ccr": 0.0,
                "max_ccr": 0.0,
                "p_autopoietic": 0.0,
                "n_measurements": 0,
                "is_operationally_autopoietic": False,
            }
        ccr_values = np.array([m.ccr for m in self.ccr_history])
        is_auto, p_auto = self.verify_operational_autopoiesis()
        return {
            "mean_ccr": float(np.mean(ccr_values)),
            "std_ccr": float(np.std(ccr_values)),
            "min_ccr": float(np.min(ccr_values)),
            "max_ccr": float(np.max(ccr_values)),
            "p_autopoietic": float(p_auto),
            "n_measurements": len(self.ccr_history),
            "is_operationally_autopoietic": is_auto,
        }

    def reset(self) -> None:
        self.ccr_history.clear()
        self.state_history.clear()
