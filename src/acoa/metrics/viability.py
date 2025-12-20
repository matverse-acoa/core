"""
Viability Index (V) - Composite Implementation
Authorea Preprint IV, Section 3.3

Reference: Autopoiesis Without Control: Black-Box Digital Organisms
and Coherence-Based Governance via ACOA (Arêas, 2024)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import warnings

import numpy as np


class ViabilityComponent(Enum):
    """Components of viability composite index."""

    UPTIME = "uptime"
    ERROR_RATE = "error_rate"
    RECOVERY_CAPACITY = "recovery_capacity"
    RESOURCE_STABILITY = "resource_stability"
    ADAPTIVE_CAPACITY = "adaptive_capacity"


@dataclass
class ViabilityResult:
    """Result container for viability measurements."""

    v_composite: float
    uptime: float
    error_rate: float
    recovery_capacity: float
    resource_stability: Optional[float] = None
    adaptive_capacity: Optional[float] = None
    contributions: Optional[Dict[str, float]] = None
    timestamp: Optional[float] = None
    label: Optional[str] = None


class ViabilityIndex:
    """
    V(t) = Σ wᵢ · componentᵢ(t)

    Implementation of composite viability index from Preprint IV:
        "A minimal composite index can be defined from observable uptime,
         error rates, resource stability, and recovery capacity."

    Default implementation (Eq. 16 in Preprint IV):
        V(t) = w₁·uptime(t) + w₂·(1-error(t)) + w₃·recovery(t)

    Parameters:
    -----------
    weights : Dict[str, float], optional
        Component weights. If None, uses default weights.

    components : List[ViabilityComponent], optional
        Components to include in composite. If None, uses default set.

    normalization : Dict[str, Tuple[float, float]], optional
        Normalization ranges for each component: (min, max)
    """

    DEFAULT_WEIGHTS = {
        ViabilityComponent.UPTIME.value: 0.4,
        ViabilityComponent.ERROR_RATE.value: 0.3,
        ViabilityComponent.RECOVERY_CAPACITY.value: 0.3,
    }

    DEFAULT_COMPONENTS = [
        ViabilityComponent.UPTIME,
        ViabilityComponent.ERROR_RATE,
        ViabilityComponent.RECOVERY_CAPACITY,
    ]

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        components: Optional[List[ViabilityComponent]] = None,
        normalization: Optional[Dict[str, Tuple[float, float]]] = None,
    ):
        self.components = components or self.DEFAULT_COMPONENTS

        if weights is None:
            self.weights = self.DEFAULT_WEIGHTS.copy()
        else:
            self.weights = weights.copy()

        self._validate_weights()

        self.normalization = normalization or {}

        self.history: List[ViabilityResult] = []

    def _validate_weights(self) -> None:
        """Validate that weights are properly configured."""
        for component in self.components:
            if component.value not in self.weights:
                raise ValueError(
                    f"Component {component.value} missing from weights"
                )

        weight_keys = set(self.weights.keys())
        component_keys = {c.value for c in self.components}
        extra_keys = weight_keys - component_keys
        if extra_keys:
            warnings.warn(
                f"Extra weights found for non-active components: {extra_keys}",
                RuntimeWarning,
            )

        total = sum(self.weights[c.value] for c in self.components)
        if not np.isclose(total, 1.0):
            for key in self.weights:
                self.weights[key] /= total

    def measure(
        self,
        uptime: float,
        error_rate: float,
        recovery_capacity: float,
        resource_stability: Optional[float] = None,
        adaptive_capacity: Optional[float] = None,
        timestamp: Optional[float] = None,
        label: Optional[str] = None,
    ) -> ViabilityResult:
        """
        Compute composite viability V(t).

        Args:
            uptime: Fraction of time operational [0, 1]
            error_rate: Rate of errors or failures [0, 1]
            recovery_capacity: Ability to recover from failures [0, 1]
            resource_stability: Stability of resources (optional) [0, 1]
            adaptive_capacity: Adaptive capacity (optional) [0, 1]
            timestamp: Optional timestamp
            label: Optional measurement label

        Returns:
            ViabilityResult with V score and component breakdown

        Raises:
            ValueError: If inputs are outside [0, 1] or invalid
        """
        self._validate_component("uptime", uptime)
        self._validate_component("error_rate", error_rate)
        self._validate_component("recovery_capacity", recovery_capacity)

        component_values = {
            ViabilityComponent.UPTIME.value: uptime,
            ViabilityComponent.ERROR_RATE.value: error_rate,
            ViabilityComponent.RECOVERY_CAPACITY.value: recovery_capacity,
        }

        if resource_stability is not None:
            self._validate_component("resource_stability", resource_stability)
            component_values[ViabilityComponent.RESOURCE_STABILITY.value] = (
                resource_stability
            )

        if adaptive_capacity is not None:
            self._validate_component("adaptive_capacity", adaptive_capacity)
            component_values[ViabilityComponent.ADAPTIVE_CAPACITY.value] = (
                adaptive_capacity
            )

        component_values[ViabilityComponent.ERROR_RATE.value] = 1.0 - error_rate

        for comp_name, value in component_values.items():
            if comp_name in self.normalization:
                min_val, max_val = self.normalization[comp_name]
                if max_val > min_val:
                    component_values[comp_name] = np.clip(
                        (value - min_val) / (max_val - min_val), 0.0, 1.0
                    )

        v_composite = 0.0
        contributions: Dict[str, float] = {}

        for component in self.components:
            comp_name = component.value
            if comp_name in component_values:
                weight = self.weights[comp_name]
                value = component_values[comp_name]

                contribution = weight * value
                v_composite += contribution
                contributions[comp_name] = contribution

        v_composite = float(np.clip(v_composite, 0.0, 1.0))

        result = ViabilityResult(
            v_composite=float(v_composite),
            uptime=uptime,
            error_rate=error_rate,
            recovery_capacity=recovery_capacity,
            resource_stability=resource_stability,
            adaptive_capacity=adaptive_capacity,
            contributions=contributions,
            timestamp=timestamp,
            label=label,
        )

        self.history.append(result)

        return result

    def measure_from_dict(self, component_dict: Dict[str, float], **kwargs) -> ViabilityResult:
        """
        Measure viability from dictionary of components.

        Args:
            component_dict: Dictionary mapping component names to values
            **kwargs: Additional arguments for measure()

        Returns:
            ViabilityResult
        """
        args = {}
        for comp in [
            "uptime",
            "error_rate",
            "recovery_capacity",
            "resource_stability",
            "adaptive_capacity",
        ]:
            if comp in component_dict:
                args[comp] = component_dict[comp]

        return self.measure(**args, **kwargs)

    def batch_measure(
        self, measurements: List[Dict[str, float]], labels: Optional[List[str]] = None
    ) -> List[ViabilityResult]:
        """
        Batch measurement of viability.

        Args:
            measurements: List of component dictionaries
            labels: Optional list of labels

        Returns:
            List of ViabilityResult objects
        """
        results: List[ViabilityResult] = []
        if labels is None:
            labels = [None] * len(measurements)

        for meas_dict, label in zip(measurements, labels):
            result = self.measure_from_dict(meas_dict, label=label)
            results.append(result)

        return results

    def get_stats(self, window: Optional[int] = None) -> Dict[str, Any]:
        """
        Get statistics from historical measurements.

        Args:
            window: Number of recent measurements to consider

        Returns:
            Dictionary of statistics
        """
        if not self.history:
            return {}

        history = self.history[-window:] if window is not None else self.history

        v_values = [h.v_composite for h in history]
        uptime_values = [h.uptime for h in history]
        error_values = [h.error_rate for h in history]
        recovery_values = [h.recovery_capacity for h in history]

        stats = {
            "mean_v": float(np.mean(v_values)),
            "std_v": float(np.std(v_values)),
            "min_v": float(np.min(v_values)),
            "max_v": float(np.max(v_values)),
            "mean_uptime": float(np.mean(uptime_values)),
            "mean_error_rate": float(np.mean(error_values)),
            "mean_recovery": float(np.mean(recovery_values)),
            "n_measurements": len(history),
        }

        if len(v_values) >= 2:
            stats["trend_v"] = float(np.polyfit(range(len(v_values)), v_values, 1)[0])

        return stats

    def threshold_check(
        self,
        v_min: float = 0.8,
        component_thresholds: Optional[Dict[str, float]] = None,
    ) -> Dict[str, bool]:
        """
        Check viability against thresholds (Preprint IV, Table 2).

        Args:
            v_min: Minimum composite viability (default 0.8 from Preprint)
            component_thresholds: Component-specific thresholds

        Returns:
            Dictionary of threshold checks
        """
        if not self.history:
            return {}

        latest = self.history[-1]

        checks: Dict[str, bool] = {
            "composite_viable": latest.v_composite >= v_min,
            "composite_value": latest.v_composite,
        }

        if component_thresholds:
            for comp, threshold in component_thresholds.items():
                comp_value = getattr(latest, comp, None)
                if comp_value is not None:
                    checks[f"{comp}_viable"] = comp_value >= threshold

        return checks

    def _validate_component(self, name: str, value: float) -> None:
        """Validate component value."""
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"{name} must be in [0, 1], got {value}")


def create_default_viability_index() -> ViabilityIndex:
    """Create viability index with default weights from Preprint IV."""
    return ViabilityIndex()


def create_custom_viability_index(
    uptime_weight: float = 0.4,
    error_weight: float = 0.3,
    recovery_weight: float = 0.3,
    include_resource_stability: bool = False,
    include_adaptive_capacity: bool = False,
) -> ViabilityIndex:
    """
    Create custom viability index.

    Args:
        uptime_weight: Weight for uptime component
        error_weight: Weight for error component
        recovery_weight: Weight for recovery component
        include_resource_stability: Include resource stability component
        include_adaptive_capacity: Include adaptive capacity component

    Returns:
        Configured ViabilityIndex
    """
    components = [
        ViabilityComponent.UPTIME,
        ViabilityComponent.ERROR_RATE,
        ViabilityComponent.RECOVERY_CAPACITY,
    ]

    weights = {
        ViabilityComponent.UPTIME.value: uptime_weight,
        ViabilityComponent.ERROR_RATE.value: error_weight,
        ViabilityComponent.RECOVERY_CAPACITY.value: recovery_weight,
    }

    if include_resource_stability:
        components.append(ViabilityComponent.RESOURCE_STABILITY)
        weights[ViabilityComponent.RESOURCE_STABILITY.value] = 0.1
        total = sum(weights.values())
        for key in weights:
            weights[key] /= total

    if include_adaptive_capacity:
        components.append(ViabilityComponent.ADAPTIVE_CAPACITY)
        weights[ViabilityComponent.ADAPTIVE_CAPACITY.value] = 0.1
        total = sum(weights.values())
        for key in weights:
            weights[key] /= total

    return ViabilityIndex(weights=weights, components=components)
