from __future__ import annotations

from pathlib import Path

import pytest


def test_project_layout_has_src() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "src" / "acoa").exists()


def test_autopoietic_core_measures_ccr() -> None:
    np = pytest.importorskip("numpy")
    from acoa.core.autopoiesis import AutopoieticCore, SystemState

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
    pytest.importorskip("numpy")
    from acoa.metrics.cvar import CVaREstimator

    estimator = CVaREstimator(alpha=0.8)
    for loss in [1.0, 2.0, 3.0, 4.0]:
        estimator.update(loss)
    estimate = estimator.compute()
    assert estimate.var >= 0
    assert estimate.cvar >= estimate.var
