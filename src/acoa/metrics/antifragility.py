"""
Antifragility Coefficient (Ω)
Authorea Preprint IV, Section 3.3

Reference: Autopoiesis Without Control: Black-Box Digital Organisms
and Coherence-Based Governance via ACOA (Arêas, 2024)

Implementation of Eq. (17) from Preprint IV:
    Ω = E[V_post-stress] / E[V_pre-stress]
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

import numpy as np


class StressType(Enum):
    """Types of stress events for categorization."""

    LOAD = "load"
    FAULT = "fault"
    ENVIRONMENTAL = "environmental"
    ADVERSARIAL = "adversarial"
    PARAMETRIC = "parametric"
    UNKNOWN = "unknown"


@dataclass
class StressEvent:
    """Representation of a stress event."""

    pre_stress_viability: float
    post_stress_viability: float
    stress_magnitude: Optional[float] = None
    stress_duration: Optional[float] = None
    stress_type: StressType = StressType.UNKNOWN
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AntifragilityResult:
    """Result container for antifragility calculations."""

    omega: float
    gain_under_stress: bool
    v_pre_stress: float
    v_post_stress: float
    n_events: int
    confidence_interval: Optional[Tuple[float, float]] = None
    p_value: Optional[float] = None
    omega_by_type: Optional[Dict[str, float]] = None
    omega_by_magnitude: Optional[Dict[str, float]] = None
    interpretation: Optional[str] = None


class AntifragilityCoefficient:
    """
    Ω = E[V_post-stress] / E[V_pre-stress]

    Implementation of Eq. (17) from Preprint IV:
        "Minimal operationalization: Ω = E[V_post-stress]/E[V_pre-stress]"

    Interpretation (Preprint IV, Table 1):
        Ω > 1: System gains from stress (antifragile)
        Ω = 1: Robust (unaffected by stress)
        Ω < 1: Fragile (degraded by stress)

    Parameters:
    -----------
    min_events : int, default=3
        Minimum number of events required for reliable Ω calculation

    bootstrap_samples : int, default=1000
        Number of bootstrap samples for confidence intervals

    alpha : float, default=0.05
        Significance level for confidence intervals
    """

    def __init__(
        self, min_events: int = 3, bootstrap_samples: int = 1000, alpha: float = 0.05
    ):
        if min_events < 2:
            raise ValueError("min_events must be at least 2")

        self.min_events = min_events
        self.bootstrap_samples = bootstrap_samples
        self.alpha = alpha

        self.events: List[StressEvent] = []

        self._cached_result: Optional[AntifragilityResult] = None

    def add_event(
        self,
        pre_stress_viability: float,
        post_stress_viability: float,
        stress_magnitude: Optional[float] = None,
        stress_duration: Optional[float] = None,
        stress_type: Union[StressType, str] = StressType.UNKNOWN,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record viability before/after a stress event.

        Args:
            pre_stress_viability: Viability before stress event ∈ [0, 1]
            post_stress_viability: Viability after stress event ∈ [0, 1]
            stress_magnitude: Optional magnitude of stress (normalized)
            stress_duration: Optional duration of stress
            stress_type: Type of stress event
            timestamp: Optional timestamp
            metadata: Optional additional metadata

        Raises:
            ValueError: If viability values invalid
        """
        for name, val in [
            ("pre_stress", pre_stress_viability),
            ("post_stress", post_stress_viability),
        ]:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{name}_viability must be in [0, 1], got {val}")

        if isinstance(stress_type, str):
            try:
                stress_type = StressType(stress_type.lower())
            except ValueError:
                stress_type = StressType.UNKNOWN

        event = StressEvent(
            pre_stress_viability=float(pre_stress_viability),
            post_stress_viability=float(post_stress_viability),
            stress_magnitude=stress_magnitude,
            stress_duration=stress_duration,
            stress_type=stress_type,
            timestamp=timestamp,
            metadata=metadata or {},
        )

        self.events.append(event)
        self._cached_result = None

    def add_batch_events(
        self,
        pre_stress_values: List[float],
        post_stress_values: List[float],
        stress_magnitudes: Optional[List[Optional[float]]] = None,
        stress_types: Optional[List[Union[StressType, str]]] = None,
        **kwargs,
    ) -> None:
        """
        Add multiple stress events in batch.

        Args:
            pre_stress_values: List of pre-stress viability values
            post_stress_values: List of post-stress viability values
            stress_magnitudes: Optional list of stress magnitudes
            stress_types: Optional list of stress types
            **kwargs: Additional arguments passed to add_event
        """
        if len(pre_stress_values) != len(post_stress_values):
            raise ValueError(
                "pre_stress_values and post_stress_values must have same length"
            )

        n_events = len(pre_stress_values)

        if stress_magnitudes is None:
            stress_magnitudes = [None] * n_events

        if stress_types is None:
            stress_types = [StressType.UNKNOWN] * n_events

        for i in range(n_events):
            self.add_event(
                pre_stress_viability=pre_stress_values[i],
                post_stress_viability=post_stress_values[i],
                stress_magnitude=stress_magnitudes[i],
                stress_type=stress_types[i],
                **kwargs,
            )

    def compute(
        self, use_bootstrap: bool = True, categorize: bool = True
    ) -> AntifragilityResult:
        """
        Compute antifragility coefficient Ω.

        Args:
            use_bootstrap: Whether to compute bootstrap confidence intervals
            categorize: Whether to compute Ω by stress type and magnitude

        Returns:
            AntifragilityResult with Ω and statistics

        Raises:
            RuntimeError: If insufficient events recorded
        """
        if len(self.events) < self.min_events:
            raise RuntimeError(
                f"Insufficient events: {len(self.events)} < {self.min_events}. "
                "Add more stress events before computing Ω."
            )

        if self._cached_result is not None:
            return self._cached_result

        pre_values = np.array([e.pre_stress_viability for e in self.events])
        post_values = np.array([e.post_stress_viability for e in self.events])

        v_pre = np.mean(pre_values)
        v_post = np.mean(post_values)

        warning_message = None

        if v_pre < 1e-10:
            omega = 0.0
            warning_message = (
                f"Pre-stress viability near zero ({v_pre:.2e}), " "Ω may be unreliable"
            )
        else:
            omega = v_post / v_pre
            if v_pre < 1e-2:
                warning_message = (
                    f"Pre-stress viability is very low ({v_pre:.2e}); "
                    "interpret Ω with caution"
                )

        if warning_message:
            warnings.warn(warning_message, RuntimeWarning)

        ci = None
        p_value = None

        if use_bootstrap and len(self.events) >= 5:
            ci, p_value = self._bootstrap_omega(pre_values, post_values)

        omega_by_type = None
        omega_by_magnitude = None

        if categorize:
            omega_by_type = self._compute_omega_by_type()
            omega_by_magnitude = self._compute_omega_by_magnitude()

        interpretation = self._interpret_omega(omega, ci)

        result = AntifragilityResult(
            omega=float(omega),
            gain_under_stress=bool(omega > 1.0),
            v_pre_stress=float(v_pre),
            v_post_stress=float(v_post),
            n_events=len(self.events),
            confidence_interval=ci,
            p_value=p_value,
            omega_by_type=omega_by_type,
            omega_by_magnitude=omega_by_magnitude,
            interpretation=interpretation,
        )

        self._cached_result = result

        return result

    def _bootstrap_omega(
        self, pre_values: np.ndarray, post_values: np.ndarray
    ) -> Tuple[Optional[Tuple[float, float]], Optional[float]]:
        """
        Compute bootstrap confidence interval for Ω.

        Returns:
            (confidence_interval, p_value)
        """
        n = len(pre_values)
        omega_samples = []

        for _ in range(self.bootstrap_samples):
            idx = np.random.choice(n, n, replace=True)
            pre_sample = pre_values[idx]
            post_sample = post_values[idx]

            v_pre = np.mean(pre_sample)
            v_post = np.mean(post_sample)

            if v_pre > 1e-10:
                omega_sample = v_post / v_pre
                omega_samples.append(omega_sample)

        if not omega_samples:
            return None, None

        alpha = self.alpha
        lower = np.percentile(omega_samples, 100 * alpha / 2)
        upper = np.percentile(omega_samples, 100 * (1 - alpha / 2))

        p_value = np.mean(np.array(omega_samples) <= 1.0)

        return (float(lower), float(upper)), float(p_value)

    def _compute_omega_by_type(self) -> Dict[str, float]:
        """Compute Ω for each stress type."""
        omega_by_type: Dict[str, float] = {}

        for stress_type in StressType:
            type_events = [e for e in self.events if e.stress_type == stress_type]

            if len(type_events) >= 2:
                pre_values = [e.pre_stress_viability for e in type_events]
                post_values = [e.post_stress_viability for e in type_events]

                v_pre = np.mean(pre_values)
                v_post = np.mean(post_values)

                if v_pre > 1e-10:
                    omega = v_post / v_pre
                    omega_by_type[stress_type.value] = float(omega)

        return omega_by_type

    def _compute_omega_by_magnitude(self) -> Dict[str, float]:
        """Compute Ω for different stress magnitude ranges."""
        if not any(e.stress_magnitude is not None for e in self.events):
            return {}

        magnitudes = [
            e.stress_magnitude for e in self.events if e.stress_magnitude is not None
        ]

        if len(magnitudes) < 4:
            return {}

        q1, q2, q3 = np.percentile(magnitudes, [25, 50, 75])

        ranges = {
            "low": (0, q1),
            "medium_low": (q1, q2),
            "medium_high": (q2, q3),
            "high": (q3, np.max(magnitudes)),
        }

        omega_by_magnitude: Dict[str, float] = {}

        for range_name, (lower, upper) in ranges.items():
            range_events = [
                e
                for e in self.events
                if e.stress_magnitude is not None
                and lower <= e.stress_magnitude <= upper
            ]

            if len(range_events) >= 2:
                pre_values = [e.pre_stress_viability for e in range_events]
                post_values = [e.post_stress_viability for e in range_events]

                v_pre = np.mean(pre_values)
                v_post = np.mean(post_values)

                if v_pre > 1e-10:
                    omega = v_post / v_pre
                    omega_by_magnitude[range_name] = float(omega)

        return omega_by_magnitude

    def _interpret_omega(
        self, omega: float, ci: Optional[Tuple[float, float]] = None
    ) -> str:
        """Create human-readable interpretation of Ω."""
        interpretations = {
            (1.2, float("inf")): "Strongly antifragile (Ω > 1.2)",
            (1.05, 1.2): "Moderately antifragile (1.05 < Ω ≤ 1.2)",
            (1.0, 1.05): "Marginally antifragile (1.0 < Ω ≤ 1.05)",
            (0.95, 1.0): "Marginally robust (0.95 < Ω ≤ 1.0)",
            (0.8, 0.95): "Moderately fragile (0.8 < Ω ≤ 0.95)",
            (0.0, 0.8): "Strongly fragile (Ω ≤ 0.8)",
        }

        base_interpretation = "Unclassified"
        for (lower, upper), description in interpretations.items():
            if lower <= omega <= upper:
                base_interpretation = description
                break

        if ci is not None:
            lower_ci, upper_ci = ci

            if lower_ci > 1.0:
                confidence = " (antifragile with high confidence)"
            elif upper_ci < 1.0:
                confidence = " (fragile with high confidence)"
            else:
                confidence = " (result not statistically significant)"
        else:
            confidence = ""

        return f"{base_interpretation}{confidence}"

    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about recorded stress events."""
        if not self.events:
            return {}

        pre_values = [e.pre_stress_viability for e in self.events]
        post_values = [e.post_stress_viability for e in self.events]
        changes = [post - pre for pre, post in zip(pre_values, post_values)]

        magnitudes = [
            e.stress_magnitude for e in self.events if e.stress_magnitude is not None
        ]

        return {
            "n_events": len(self.events),
            "mean_pre_stress": float(np.mean(pre_values)),
            "std_pre_stress": float(np.std(pre_values)),
            "mean_post_stress": float(np.mean(post_values)),
            "std_post_stress": float(np.std(post_values)),
            "mean_change": float(np.mean(changes)),
            "positive_changes": sum(1 for c in changes if c > 0),
            "negative_changes": sum(1 for c in changes if c < 0),
            "has_magnitude_data": len(magnitudes) > 0,
            "n_with_magnitude": len(magnitudes),
            "event_types": {
                t.value: sum(1 for e in self.events if e.stress_type == t)
                for t in StressType
            },
        }

    def clear_events(self) -> None:
        """Clear all recorded stress events."""
        self.events.clear()
        self._cached_result = None

    def filter_events(
        self,
        min_pre_stress: Optional[float] = None,
        max_pre_stress: Optional[float] = None,
        stress_types: Optional[List[StressType]] = None,
    ) -> List[StressEvent]:
        """
        Filter events based on criteria.

        Returns:
            Filtered list of events (does not modify stored events)
        """
        filtered = self.events.copy()

        if min_pre_stress is not None:
            filtered = [e for e in filtered if e.pre_stress_viability >= min_pre_stress]

        if max_pre_stress is not None:
            filtered = [e for e in filtered if e.pre_stress_viability <= max_pre_stress]

        if stress_types is not None:
            filtered = [e for e in filtered if e.stress_type in stress_types]

        return filtered


def create_antifragility_monitor(
    min_events: int = 3, **kwargs
) -> AntifragilityCoefficient:
    """
    Create an AntifragilityCoefficient monitor.

    Args:
        min_events: Minimum events for reliable computation
        **kwargs: Additional arguments for AntifragilityCoefficient

    Returns:
        Configured antifragility monitor
    """
    return AntifragilityCoefficient(min_events=min_events, **kwargs)
