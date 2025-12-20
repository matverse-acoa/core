"""
Unit tests for Antifragility Coefficient (Ω) implementation.
"""

import numpy as np
import pytest

from acoa.metrics.antifragility import (
    AntifragilityCoefficient,
    StressType,
    create_antifragility_monitor,
)


class TestAntifragilityCoefficient:
    """Test suite for AntifragilityCoefficient class."""

    def test_initialization(self):
        """Test basic initialization."""
        omega = AntifragilityCoefficient(min_events=3)
        assert omega.min_events == 3
        assert len(omega.events) == 0

    def test_invalid_min_events(self):
        """Test invalid min_events parameter."""
        with pytest.raises(ValueError):
            AntifragilityCoefficient(min_events=0)
        with pytest.raises(ValueError):
            AntifragilityCoefficient(min_events=1)

    def test_add_event(self):
        """Test adding individual stress events."""
        omega = AntifragilityCoefficient(min_events=2)

        omega.add_event(
            pre_stress_viability=0.8,
            post_stress_viability=0.9,
            stress_type=StressType.LOAD,
            stress_magnitude=0.5,
        )

        assert len(omega.events) == 1
        event = omega.events[0]
        assert event.pre_stress_viability == 0.8
        assert event.post_stress_viability == 0.9
        assert event.stress_type == StressType.LOAD
        assert event.stress_magnitude == 0.5

    def test_add_event_validation(self):
        """Test validation of viability values."""
        omega = AntifragilityCoefficient(min_events=2)

        omega.add_event(pre_stress_viability=0.5, post_stress_viability=0.6)

        with pytest.raises(ValueError):
            omega.add_event(pre_stress_viability=1.5, post_stress_viability=0.6)

        with pytest.raises(ValueError):
            omega.add_event(pre_stress_viability=0.5, post_stress_viability=-0.1)

    def test_add_batch_events(self):
        """Test adding multiple events in batch."""
        omega = AntifragilityCoefficient(min_events=3)

        pre_values = [0.8, 0.7, 0.9]
        post_values = [0.9, 0.6, 1.0]
        stress_types = [StressType.LOAD, StressType.FAULT, StressType.LOAD]

        omega.add_batch_events(
            pre_stress_values=pre_values,
            post_stress_values=post_values,
            stress_types=stress_types,
        )

        assert len(omega.events) == 3
        assert omega.events[0].stress_type == StressType.LOAD
        assert omega.events[1].stress_type == StressType.FAULT

    def test_add_batch_validation(self):
        """Test validation of batch events."""
        omega = AntifragilityCoefficient(min_events=2)

        with pytest.raises(ValueError):
            omega.add_batch_events(
                pre_stress_values=[0.8, 0.7],
                post_stress_values=[0.9],
            )

    def test_compute_antifragile(self):
        """Test Ω computation for antifragile system (Ω > 1)."""
        omega = AntifragilityCoefficient(min_events=3)

        omega.add_batch_events(
            pre_stress_values=[0.8, 0.7, 0.9],
            post_stress_values=[0.9, 0.8, 1.0],
        )

        result = omega.compute(use_bootstrap=False)

        assert result.omega > 1.0
        assert result.gain_under_stress is True
        assert result.n_events == 3
        assert result.v_pre_stress < result.v_post_stress

        assert "antifragile" in result.interpretation.lower()

    def test_compute_fragile(self):
        """Test Ω computation for fragile system (Ω < 1)."""
        omega = AntifragilityCoefficient(min_events=3)

        omega.add_batch_events(
            pre_stress_values=[0.8, 0.7, 0.9],
            post_stress_values=[0.7, 0.6, 0.8],
        )

        result = omega.compute(use_bootstrap=False)

        assert result.omega < 1.0
        assert result.gain_under_stress is False
        assert result.v_pre_stress > result.v_post_stress

        assert "fragile" in result.interpretation.lower()

    def test_compute_robust(self):
        """Test Ω computation for robust system (Ω ≈ 1)."""
        omega = AntifragilityCoefficient(min_events=3)

        omega.add_batch_events(
            pre_stress_values=[0.8, 0.7, 0.9],
            post_stress_values=[0.8, 0.7, 0.9],
        )

        result = omega.compute(use_bootstrap=False)

        assert result.omega == pytest.approx(1.0, abs=1e-10)
        assert result.gain_under_stress is False
        assert result.v_pre_stress == pytest.approx(result.v_post_stress)

    def test_insufficient_events(self):
        """Test error when insufficient events."""
        omega = AntifragilityCoefficient(min_events=3)

        omega.add_batch_events(
            pre_stress_values=[0.8, 0.7],
            post_stress_values=[0.9, 0.8],
        )

        with pytest.raises(RuntimeError):
            omega.compute()

    def test_near_zero_pre_stress(self):
        """Test handling of near-zero pre-stress viability."""
        omega = AntifragilityCoefficient(min_events=2)

        omega.add_batch_events(
            pre_stress_values=[0.001, 0.002],
            post_stress_values=[0.9, 0.8],
        )

        with pytest.warns(RuntimeWarning):
            result = omega.compute(use_bootstrap=False)

        assert result.omega > 1.0

    def test_bootstrap_confidence(self):
        """Test bootstrap confidence interval computation."""
        omega = AntifragilityCoefficient(min_events=5, bootstrap_samples=100)

        np.random.seed(42)
        n_events = 20

        pre_values = np.random.uniform(0.7, 0.9, n_events)
        post_values = pre_values + np.random.uniform(0.05, 0.15, n_events)
        post_values = np.clip(post_values, 0.0, 1.0)

        omega.add_batch_events(
            pre_stress_values=pre_values.tolist(),
            post_stress_values=post_values.tolist(),
        )

        result = omega.compute(use_bootstrap=True)

        assert result.confidence_interval is not None
        assert result.p_value is not None

        lower, upper = result.confidence_interval

        assert lower > 1.0 or upper > 1.0
        assert result.p_value < 0.05

    def test_categorization(self):
        """Test Ω computation by stress type and magnitude."""
        omega = AntifragilityCoefficient(min_events=6)

        events_data = [
            (0.8, 0.9, StressType.LOAD, 0.3),
            (0.7, 0.8, StressType.LOAD, 0.4),
            (0.9, 0.8, StressType.FAULT, 0.7),
            (0.8, 0.7, StressType.FAULT, 0.8),
            (0.6, 0.7, StressType.ENVIRONMENTAL, 0.5),
            (0.7, 0.8, StressType.ENVIRONMENTAL, 0.6),
        ]

        for pre, post, stress_type, magnitude in events_data:
            omega.add_event(
                pre_stress_viability=pre,
                post_stress_viability=post,
                stress_type=stress_type,
                stress_magnitude=magnitude,
            )

        result = omega.compute(categorize=True)

        assert result.omega_by_type is not None
        assert result.omega_by_magnitude is not None

        assert "load" in result.omega_by_type
        assert "fault" in result.omega_by_type
        assert "environmental" in result.omega_by_type

        assert result.omega_by_type["load"] > 1.0
        assert result.omega_by_type["fault"] < 1.0

        assert any(
            "low" in key or "high" in key for key in result.omega_by_magnitude.keys()
        )

    def test_event_statistics(self):
        """Test event statistics computation."""
        omega = AntifragilityCoefficient(min_events=3)

        omega.add_batch_events(
            pre_stress_values=[0.8, 0.7, 0.9],
            post_stress_values=[0.9, 0.6, 1.0],
            stress_types=[StressType.LOAD, StressType.FAULT, StressType.LOAD],
        )

        stats = omega.get_event_statistics()

        assert stats["n_events"] == 3
        assert "mean_pre_stress" in stats
        assert "mean_post_stress" in stats
        assert "mean_change" in stats
        assert stats["positive_changes"] == 2
        assert stats["negative_changes"] == 1
        assert "event_types" in stats
        assert stats["event_types"]["load"] == 2
        assert stats["event_types"]["fault"] == 1

    def test_filter_events(self):
        """Test event filtering."""
        omega = AntifragilityCoefficient(min_events=2)

        omega.add_event(
            pre_stress_viability=0.9,
            post_stress_viability=1.0,
            stress_type=StressType.LOAD,
        )
        omega.add_event(
            pre_stress_viability=0.6,
            post_stress_viability=0.7,
            stress_type=StressType.FAULT,
        )
        omega.add_event(
            pre_stress_viability=0.8,
            post_stress_viability=0.9,
            stress_type=StressType.LOAD,
        )

        filtered = omega.filter_events(min_pre_stress=0.7)
        assert len(filtered) == 2

        filtered = omega.filter_events(stress_types=[StressType.LOAD])
        assert len(filtered) == 2
        assert all(e.stress_type == StressType.LOAD for e in filtered)

    def test_clear_events(self):
        """Test clearing events."""
        omega = AntifragilityCoefficient(min_events=2)

        omega.add_batch_events(
            pre_stress_values=[0.8, 0.7],
            post_stress_values=[0.9, 0.8],
        )

        assert len(omega.events) == 2
        omega.clear_events()
        assert len(omega.events) == 0

        with pytest.raises(RuntimeError):
            omega.compute()


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_antifragility_monitor(self):
        """Test create_antifragility_monitor."""
        monitor = create_antifragility_monitor(
            min_events=5, bootstrap_samples=500, alpha=0.01
        )

        assert monitor.min_events == 5
        assert monitor.bootstrap_samples == 500
        assert monitor.alpha == 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
