"""
Coherence Index (Ψ) - Dual Implementation
Authorea Preprint IV, Section 3.3

Reference: Autopoiesis Without Control: Black-Box Digital Organisms
and Coherence-Based Governance via ACOA (Arêas, 2024)
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
import warnings

import numpy as np
from scipy.special import kl_div


@dataclass
class CoherenceResult:
    """Result container for coherence measurements."""

    psi_kl: float
    psi_composite: float
    d_kl: float
    p_current_norm: np.ndarray
    p_reference_norm: np.ndarray


class CoherenceIndex:
    """
    Ψ(t) = 1 - D_KL(P_t || P_ref) / D_max

    Implementation of Equation (15) from Preprint IV:
        "One minimal operationalization: Ψ(t) = 1 - D_KL(P_t || P_ref)/D_max
         where P_t is a distribution of outputs (or behavioral tokens) at
         time t, and P_ref is a reference baseline."

    Parameters:
    -----------
    d_max : float, default=10.0
        Maximum KL divergence for normalization.
        According to Preprint IV: "D_max is chosen as an upper bound
        on plausible divergence."

    eps : float, default=1e-12
        Numerical stability epsilon for zero probabilities.

    track_history : bool, default=False
        Whether to store historical measurements.
    """

    def __init__(
        self, d_max: float = 10.0, eps: float = 1e-12, track_history: bool = False
    ):
        if d_max <= 0:
            raise ValueError("d_max must be positive")
        self.d_max = d_max
        self.eps = eps
        self.track_history = track_history

        self.p_ref: Optional[np.ndarray] = None
        self.history: list[Dict[str, Any]] = []

    def set_reference(
        self, p_reference: np.ndarray, label: Optional[str] = None
    ) -> None:
        """
        Set reference distribution for future measurements.

        Args:
            p_reference: Reference probability distribution
            label: Optional label for this reference distribution

        Raises:
            ValueError: If distribution is invalid
        """
        p_ref = self._validate_distribution(p_reference, label="reference")
        self.p_ref = self._normalize(p_ref)

        if self.track_history:
            self.history.append(
                {
                    "timestamp": len(self.history),
                    "label": label,
                    "action": "set_reference",
                    "p_reference": self.p_ref.copy(),
                }
            )

    def measure(
        self,
        p_current: np.ndarray,
        p_reference: Optional[np.ndarray] = None,
        label: Optional[str] = None,
    ) -> CoherenceResult:
        """
        Measure coherence via KL divergence (Preprint IV, Eq. 15).

        Args:
            p_current: Current output/behavioral distribution
            p_reference: Reference baseline (uses stored if None)
            label: Optional identifier for this measurement

        Returns:
            CoherenceResult with Ψ score and supporting data

        Raises:
            RuntimeError: If no reference available
            ValueError: If distributions invalid
        """
        p_curr = self._validate_distribution(p_current, label="current")
        p_curr_norm = self._normalize(p_curr)

        if p_reference is None:
            if self.p_ref is None:
                self.set_reference(p_curr, label="initial_reference")
            p_ref_norm = self.p_ref.copy() if self.p_ref is not None else p_curr_norm
        else:
            p_ref = self._validate_distribution(p_reference, label="provided_reference")
            p_ref_norm = self._normalize(p_ref)

        d_kl = self._compute_kl_divergence(p_curr_norm, p_ref_norm)

        if d_kl > self.d_max:
            warnings.warn(
                f"KL divergence {d_kl:.4f} exceeds D_max {self.d_max}. "
                "Consider increasing D_max or re-evaluating distributions.",
                RuntimeWarning,
            )

        psi_kl = 1.0 - min(d_kl / self.d_max, 1.0)

        result = CoherenceResult(
            psi_kl=float(psi_kl),
            psi_composite=float(psi_kl),
            d_kl=float(d_kl),
            p_current_norm=p_curr_norm,
            p_reference_norm=p_ref_norm,
        )

        if self.track_history:
            self.history.append(
                {
                    "timestamp": len(self.history),
                    "psi_kl": psi_kl,
                    "d_kl": d_kl,
                    "label": label,
                    "p_current": p_curr_norm.copy(),
                    "p_reference": p_ref_norm.copy(),
                }
            )

        return result

    def batch_measure(
        self, distributions: list[np.ndarray], labels: Optional[list[str]] = None
    ) -> list[CoherenceResult]:
        """
        Measure coherence for multiple distributions.

        Args:
            distributions: List of distributions to measure
            labels: Optional list of labels

        Returns:
            List of CoherenceResult objects
        """
        results: list[CoherenceResult] = []
        if labels is None:
            labels = [None] * len(distributions)

        for p, label in zip(distributions, labels):
            result = self.measure(p, label=label)
            results.append(result)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from historical measurements."""
        if not self.history:
            return {}

        psi_values = [h["psi_kl"] for h in self.history if "psi_kl" in h]
        d_kl_values = [h["d_kl"] for h in self.history if "d_kl" in h]

        if not psi_values:
            return {}

        return {
            "mean_psi": float(np.mean(psi_values)),
            "std_psi": float(np.std(psi_values)),
            "min_psi": float(np.min(psi_values)),
            "max_psi": float(np.max(psi_values)),
            "mean_d_kl": float(np.mean(d_kl_values)),
            "n_measurements": len(psi_values),
        }

    def _validate_distribution(
        self, p: np.ndarray, label: str = "distribution"
    ) -> np.ndarray:
        """Validate probability distribution."""
        p_array = np.asarray(p, dtype=np.float64)

        if p_array.ndim != 1:
            raise ValueError(f"{label} must be 1D array")

        if len(p_array) < 2:
            raise ValueError(f"{label} must have at least 2 elements")

        if np.any(p_array < 0):
            raise ValueError(f"{label} contains negative values")

        if np.all(p_array == 0):
            raise ValueError(f"{label} is all zeros")

        return p_array

    def _normalize(self, p: np.ndarray) -> np.ndarray:
        """Normalize distribution with numerical stability."""
        p_norm = p.copy()
        p_norm[p_norm < self.eps] = self.eps
        total = np.sum(p_norm)

        if total <= 0:
            raise ValueError("Distribution sums to non-positive value")

        return p_norm / total

    def _compute_kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """
        Compute KL divergence D_KL(P || Q) with numerical stability.

        Uses scipy.special.kl_div which handles log(0) cases.
        """
        if p.shape != q.shape:
            raise ValueError("Distributions must have same shape")

        kl_terms = kl_div(p, q)
        d_kl = np.sum(kl_terms)

        return max(d_kl, 0.0)


def create_coherence_index(
    d_max: float = 10.0, p_reference: Optional[np.ndarray] = None, **kwargs
) -> CoherenceIndex:
    """
    Create and optionally initialize a CoherenceIndex.

    Args:
        d_max: Maximum KL divergence for normalization
        p_reference: Optional reference distribution to set
        **kwargs: Additional arguments for CoherenceIndex

    Returns:
        Configured CoherenceIndex instance
    """
    psi = CoherenceIndex(d_max=d_max, **kwargs)
    if p_reference is not None:
        psi.set_reference(p_reference)
    return psi
