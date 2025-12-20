"""
Unit tests for Coherence Index (Ψ) implementation.
"""

import numpy as np
import pytest
from scipy.stats import entropy

from acoa.metrics.coherence import CoherenceIndex, create_coherence_index


class TestCoherenceIndex:
    """Test suite for CoherenceIndex class."""

    def test_initialization(self):
        """Test basic initialization."""
        psi = CoherenceIndex(d_max=5.0)
        assert psi.d_max == 5.0
        assert psi.p_ref is None

    def test_invalid_d_max(self):
        """Test invalid d_max parameter."""
        with pytest.raises(ValueError):
            CoherenceIndex(d_max=0)
        with pytest.raises(ValueError):
            CoherenceIndex(d_max=-1.0)

    def test_perfect_coherence_with_self(self):
        """Ψ(P, P) = 1.0 (perfect coherence with self)."""
        psi = CoherenceIndex()
        p = np.array([0.5, 0.3, 0.2])

        result = psi.measure(p, p)
        assert result.psi_kl == pytest.approx(1.0, abs=1e-10)
        assert result.d_kl == pytest.approx(0.0, abs=1e-10)

    def test_coherence_degradation(self):
        """Coherence decreases with divergence."""
        psi = CoherenceIndex(d_max=2.0)

        p_ref = np.array([0.5, 0.3, 0.2])
        p_degraded = np.array([0.2, 0.3, 0.5])

        result = psi.measure(p_degraded, p_ref)

        assert 0.0 <= result.psi_kl < 1.0
        assert result.d_kl > 0.0

        expected_d_kl = entropy(p_degraded, p_ref)
        assert result.d_kl == pytest.approx(expected_d_kl, abs=1e-10)

    def test_numerical_stability(self):
        """Handle edge cases gracefully."""
        psi = CoherenceIndex()

        p_sparse = np.array([0.99, 0.005, 0.005])
        p_ref = np.array([0.33, 0.33, 0.34])

        result = psi.measure(p_sparse, p_ref)
        assert np.isfinite(result.psi_kl)
        assert 0.0 <= result.psi_kl <= 1.0

        with pytest.raises(ValueError):
            psi.measure(np.array([0, 0, 0]), p_ref)

    def test_reference_setting(self):
        """Test setting and using reference distribution."""
        psi = CoherenceIndex()
        p_ref = np.array([0.4, 0.4, 0.2])

        psi.set_reference(p_ref)
        assert psi.p_ref is not None

        p_current = np.array([0.3, 0.4, 0.3])
        result1 = psi.measure(p_current)

        result2 = psi.measure(p_current, p_ref)

        assert result1.psi_kl == pytest.approx(result2.psi_kl)
        assert result1.d_kl == pytest.approx(result2.d_kl)

    def test_normalization(self):
        """Test that distributions are normalized."""
        psi = CoherenceIndex()

        p1 = np.array([1, 2, 3])
        p2 = np.array([2, 2, 2])

        result = psi.measure(p1, p2)
        assert np.isclose(np.sum(result.p_current_norm), 1.0)
        assert np.isclose(np.sum(result.p_reference_norm), 1.0)

    def test_batch_measurement(self):
        """Test batch coherence measurement."""
        psi = CoherenceIndex(d_max=10.0)
        p_ref = np.array([0.5, 0.5])
        psi.set_reference(p_ref)

        distributions = [
            np.array([0.5, 0.5]),
            np.array([0.6, 0.4]),
            np.array([0.9, 0.1]),
        ]

        results = psi.batch_measure(distributions)
        assert len(results) == 3

        assert results[0].psi_kl == pytest.approx(1.0)
        assert results[0].psi_kl > results[1].psi_kl
        assert results[1].psi_kl > results[2].psi_kl

    def test_history_tracking(self):
        """Test history tracking functionality."""
        psi = CoherenceIndex(track_history=True)
        p_ref = np.array([0.5, 0.5])

        p1 = np.array([0.5, 0.5])
        p2 = np.array([0.6, 0.4])

        psi.measure(p1, p_ref, label="measurement_1")
        psi.measure(p2, p_ref, label="measurement_2")

        assert len(psi.history) == 2
        assert psi.history[0]["label"] == "measurement_1"
        assert psi.history[1]["label"] == "measurement_2"

        stats = psi.get_stats()
        assert stats["n_measurements"] == 2
        assert "mean_psi" in stats

    def test_d_max_warning(self):
        """Test warning when KL exceeds D_max."""
        psi = CoherenceIndex(d_max=0.1)

        p_ref = np.array([0.9, 0.1])
        p_current = np.array([0.1, 0.9])

        with pytest.warns(RuntimeWarning):
            result = psi.measure(p_current, p_ref)
            assert result.psi_kl == 0.0

    def test_factory_function(self):
        """Test create_coherence_index factory."""
        p_ref = np.array([0.7, 0.3])
        psi = create_coherence_index(d_max=5.0, p_reference=p_ref)

        assert psi.p_ref is not None
        assert psi.d_max == 5.0

        p_current = np.array([0.6, 0.4])
        result = psi.measure(p_current)
        assert 0.0 <= result.psi_kl <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
