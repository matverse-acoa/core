"""
Unit tests for Viability Index (V) implementation.
"""

import numpy as np
import pytest

from acoa.metrics.viability import (
    ViabilityComponent,
    ViabilityIndex,
    create_custom_viability_index,
    create_default_viability_index,
)


class TestViabilityIndex:
    """Test suite for ViabilityIndex class."""

    def test_default_initialization(self):
        """Test initialization with default weights."""
        vi = ViabilityIndex()

        total = sum(vi.weights.values())
        assert np.isclose(total, 1.0)

        assert len(vi.components) == 3
        comp_names = {c.value for c in vi.components}
        assert {"uptime", "error_rate", "recovery_capacity"} == comp_names

    def test_custom_weights(self):
        """Test initialization with custom weights."""
        weights = {
            "uptime": 0.5,
            "error_rate": 0.3,
            "recovery_capacity": 0.2,
        }

        vi = ViabilityIndex(weights=weights)
        assert vi.weights["uptime"] == 0.5
        assert vi.weights["error_rate"] == 0.3
        assert vi.weights["recovery_capacity"] == 0.2

    def test_weight_normalization(self):
        """Test that weights are normalized to sum to 1."""
        weights = {
            "uptime": 1.0,
            "error_rate": 1.0,
            "recovery_capacity": 1.0,
        }

        vi = ViabilityIndex(weights=weights)
        total = sum(vi.weights.values())
        assert np.isclose(total, 1.0)
        assert np.allclose(list(vi.weights.values()), 1 / 3)

    def test_basic_measurement(self):
        """Test basic viability measurement."""
        vi = ViabilityIndex()

        result = vi.measure(uptime=1.0, error_rate=0.0, recovery_capacity=1.0)

        assert result.v_composite == pytest.approx(1.0, abs=1e-10)
        assert result.uptime == 1.0
        assert result.error_rate == 0.0
        assert result.recovery_capacity == 1.0
        assert result.contributions is not None

        contributions = result.contributions
        assert "uptime" in contributions
        assert "error_rate" in contributions
        assert "recovery_capacity" in contributions

    def test_error_rate_transformation(self):
        """Test that error rate is transformed (1 - error_rate)."""
        vi = ViabilityIndex()

        result1 = vi.measure(uptime=0.0, error_rate=0.0, recovery_capacity=0.0)
        error_contrib1 = result1.contributions["error_rate"]

        result2 = vi.measure(uptime=0.0, error_rate=1.0, recovery_capacity=0.0)
        error_contrib2 = result2.contributions["error_rate"]

        assert error_contrib1 > 0
        assert error_contrib2 == 0.0

    def test_component_validation(self):
        """Test validation of component values."""
        vi = ViabilityIndex()

        vi.measure(uptime=0.5, error_rate=0.5, recovery_capacity=0.5)

        with pytest.raises(ValueError):
            vi.measure(uptime=1.5, error_rate=0.5, recovery_capacity=0.5)

        with pytest.raises(ValueError):
            vi.measure(uptime=0.5, error_rate=-0.1, recovery_capacity=0.5)

    def test_optional_components(self):
        """Test measurement with optional components."""
        vi = ViabilityIndex()

        result = vi.measure(
            uptime=0.9,
            error_rate=0.1,
            recovery_capacity=0.8,
            resource_stability=0.7,
            adaptive_capacity=0.6,
        )

        assert result.resource_stability == 0.7
        assert result.adaptive_capacity == 0.6
        assert result.v_composite < 1.0

    def test_measure_from_dict(self):
        """Test measurement from dictionary."""
        vi = ViabilityIndex()

        component_dict = {
            "uptime": 0.95,
            "error_rate": 0.05,
            "recovery_capacity": 0.8,
        }

        result = vi.measure_from_dict(component_dict)
        assert result.v_composite > 0.0
        assert result.uptime == 0.95
        assert result.error_rate == 0.05

    def test_batch_measurement(self):
        """Test batch measurement."""
        vi = ViabilityIndex()

        measurements = [
            {"uptime": 1.0, "error_rate": 0.0, "recovery_capacity": 1.0},
            {"uptime": 0.9, "error_rate": 0.1, "recovery_capacity": 0.8},
            {"uptime": 0.8, "error_rate": 0.2, "recovery_capacity": 0.6},
        ]

        results = vi.batch_measure(measurements, labels=["a", "b", "c"])

        assert len(results) == 3
        assert results[0].v_composite > results[1].v_composite
        assert results[1].v_composite > results[2].v_composite
        assert results[0].label == "a"

    def test_history_tracking(self):
        """Test history tracking."""
        vi = ViabilityIndex()

        for i in range(3):
            vi.measure(
                uptime=0.9 - i * 0.1,
                error_rate=0.1 + i * 0.1,
                recovery_capacity=0.8 - i * 0.1,
                label=f"test_{i}",
            )

        assert len(vi.history) == 3
        assert vi.history[0].label == "test_0"
        assert vi.history[2].v_composite < vi.history[0].v_composite

    def test_statistics(self):
        """Test statistics computation."""
        vi = ViabilityIndex()

        for _ in range(5):
            vi.measure(uptime=0.9, error_rate=0.1, recovery_capacity=0.8)

        stats = vi.get_stats()

        assert "mean_v" in stats
        assert "std_v" in stats
        assert "n_measurements" in stats
        assert stats["n_measurements"] == 5

        window_stats = vi.get_stats(window=2)
        assert window_stats["n_measurements"] == 2

    def test_threshold_check(self):
        """Test threshold checking."""
        vi = ViabilityIndex()

        vi.measure(uptime=0.95, error_rate=0.05, recovery_capacity=0.9)
        vi.measure(uptime=0.7, error_rate=0.3, recovery_capacity=0.6)

        checks = vi.threshold_check(v_min=0.8)

        assert "composite_viable" in checks
        assert "composite_value" in checks

        latest = vi.history[-1]
        if latest.v_composite >= 0.8:
            assert checks["composite_viable"] is True
        else:
            assert checks["composite_viable"] is False

    def test_normalization(self):
        """Test component normalization."""
        normalization = {
            "uptime": (0.5, 1.0),
        }

        vi = ViabilityIndex(normalization=normalization)

        result = vi.measure(uptime=0.75, error_rate=0.1, recovery_capacity=0.8)

        assert result.contributions["uptime"] == pytest.approx(0.4 * 0.5)


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_default(self):
        """Test create_default_viability_index."""
        vi = create_default_viability_index()
        assert isinstance(vi, ViabilityIndex)
        assert len(vi.components) == 3

    def test_create_custom(self):
        """Test create_custom_viability_index."""
        vi = create_custom_viability_index(
            uptime_weight=0.6,
            error_weight=0.2,
            recovery_weight=0.2,
            include_resource_stability=True,
            include_adaptive_capacity=True,
        )

        assert len(vi.components) == 5

        total = sum(vi.weights.values())
        assert np.isclose(total, 1.0)

        uptime_contrib = vi.weights.get("uptime", 0)
        assert uptime_contrib > 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
