from __future__ import annotations

import numpy as np

from acoa.core.autopoiesis import AutopoieticCore, SystemState
from acoa.metrics.cvar import CVaREstimator


def test_autopoietic_core_measures_ccr() -> None:
    core = AutopoieticCore()
    state = SystemState(
        internal=np.array([1.0, 2.0]),
        external=np.array([0.5]),
        output=np.array([1.5, 2.5]),
        timestamp=1.0,
    )
    measurement = core.measure_ccr(state)
    assert measurement.ccr >= 0
    stats = core.get_statistics()
    assert stats["n_measurements"] == 1


def test_cvar_estimator_computes_values() -> None:
    estimator = CVaREstimator(alpha=0.8)
    for loss in [1.0, 2.0, 3.0, 4.0]:
        estimator.update(loss)
    estimate = estimator.compute()
    assert estimate.var >= 0
    assert estimate.cvar >= estimate.var
