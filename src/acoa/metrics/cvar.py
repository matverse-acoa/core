"""Estimador CVaR (streaming/rolling) fiel à especificação."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass
class CVaREstimate:
    cvar: float
    var: float
    alpha: float
    n_samples: int
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None


class CVaREstimator:
    def __init__(self, alpha: float = 0.95, buffer_size: int = 10000) -> None:
        if not 0 < alpha < 1:
            raise ValueError("alpha deve estar em (0,1)")
        self.alpha = alpha
        self.buffer: deque[float] = deque(maxlen=buffer_size)
        self._sorted_losses: Optional[np.ndarray] = None
        self._dirty = True

    def update(self, loss: float) -> None:
        if loss < 0:
            raise ValueError("loss must be non-negative")
        self.buffer.append(loss)
        self._dirty = True

    def compute(self) -> CVaREstimate:
        if len(self.buffer) == 0:
            raise RuntimeError("empty buffer")
        if self._dirty:
            self._sorted_losses = np.sort(np.array(self.buffer))
            self._dirty = False
        if self._sorted_losses is None:
            raise RuntimeError("loss buffer not initialized")
        n = len(self._sorted_losses)
        var_index = min(int(self.alpha * n), n - 1)
        var = float(self._sorted_losses[var_index])
        tail = self._sorted_losses[var_index:]
        cvar = float(np.mean(tail)) if len(tail) > 0 else 0.0
        return CVaREstimate(cvar=cvar, var=var, alpha=self.alpha, n_samples=n)

    def confidence_interval(
        self, confidence: float = 0.95, n_bootstrap: int = 1000
    ) -> Tuple[float, float]:
        if len(self.buffer) == 0:
            return (0.0, 0.0)
        losses = np.array(self.buffer)
        samples = []
        for _ in range(n_bootstrap):
            sample = np.random.choice(losses, size=len(losses), replace=True)
            sorted_sample = np.sort(sample)
            var_idx = min(int(self.alpha * len(sample)), len(sample) - 1)
            tail = sorted_sample[var_idx:]
            samples.append(np.mean(tail) if len(tail) > 0 else 0.0)
        lower = float(np.percentile(samples, (1 - confidence) / 2 * 100))
        upper = float(np.percentile(samples, (1 + confidence) / 2 * 100))
        return (lower, upper)

    def get_tail_distribution(self) -> np.ndarray:
        if len(self.buffer) == 0:
            return np.array([])
        est = self.compute()
        return np.array(
            [loss_value for loss_value in self.buffer if loss_value > est.var]
        )
