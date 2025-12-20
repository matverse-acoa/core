# 🧬 ACOA Core: Adaptive Coherence-Oriented Audit

[![arXiv](https://img.shields.io/badge/Preprint-Authorea-blue)](https://www.authorea.com/doi/full/10.22541/au.XXXXXXX)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0008--2973--4047-green)](https://orcid.org/0009-0008-2973-4047)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/matverse-acoa/core/actions/workflows/test.yml/badge.svg)](https://github.com/matverse-acoa/core/actions/workflows/test.yml)

**Reference implementation of the Adaptive Coherence-Oriented Audit (ACOA)** – a post-control governance framework for black-box autopoietic digital organisms.

Based on **Preprint IV**: *Autopoiesis Without Control: Black-Box Digital Organisms and Coherence-Based Governance via ACOA* (Arêas, 2024).

> **Cite this work**:
> Arêas, G. (2024). Autopoiesis Without Control: Black-Box Digital Organisms and Coherence-Based Governance via ACOA. Authorea Preprint. https://doi.org/10.22541/au.XXXXXXX

## 🎯 Core Invariants (Preprint IV, Section 3.2)

ACOA monitors five fundamental invariants of autopoietic digital organisms:

| Invariant | Symbol | Definition | Threshold | Reference |
|-----------|--------|------------|-----------|-----------|
| **Coherence** | Ψ | `1 - D_KL(P_t || P_ref)/D_max` | ≥ 0.85 | Eq. (15) |
| **Antifragility** | Ω | `E[V_post] / E[V_pre]` | > 1.0 | Eq. (17) |
| **Tail Risk** | CVaR | `E[L | L ≥ VaR_α]` | ≤ 0.30 | Eq. (13) |
| **Causal Closure** | CCR | `||∂ρ/∂x|| / ||∂ρ/∂u||` | > 1.0 | Eq. (11) |
| **Viability** | V | `w₁·uptime + w₂·(1-err) + w₃·rec` | ≥ 0.80 | Eq. (16) |

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/matverse-acoa/core.git
cd core

# Install with pip
pip install -e .

# Or with poetry
poetry install

# Install development dependencies
pip install -e ".[dev]"
```

## 🚀 Quick Start

```python
import numpy as np
from acoa.metrics.coherence import CoherenceIndex
from acoa.metrics.viability import ViabilityIndex
from acoa.metrics.antifragility import AntifragilityCoefficient

# 1. Measure Coherence (Ψ)
psi = CoherenceIndex(d_max=10.0)
p_ref = np.array([0.5, 0.3, 0.2])
p_current = np.array([0.4, 0.3, 0.3])
result = psi.measure(p_current, p_ref)
print(f"Coherence Ψ = {result.psi_kl:.3f}")

# 2. Measure Viability (V)
viability = ViabilityIndex()
v_result = viability.measure(
    uptime=0.95,
    error_rate=0.05,
    recovery_capacity=0.8
)
print(f"Viability V = {v_result.v_composite:.3f}")

# 3. Measure Antifragility (Ω)
omega = AntifragilityCoefficient(min_events=3)
omega.add_batch_events(
    pre_stress_values=[0.8, 0.7, 0.9],
    post_stress_values=[0.9, 0.8, 1.0]
)
result = omega.compute()
print(f"Antifragility Ω = {result.omega:.3f}")
print(f"Interpretation: {result.interpretation}")
```

## 📚 API Reference

### Coherence Index (Ψ)

```python
from acoa.metrics.coherence import CoherenceIndex

# Initialize with reference distribution
psi = CoherenceIndex(d_max=10.0)
psi.set_reference(reference_distribution)

# Measure coherence
result = psi.measure(current_distribution)

# Access results
print(f"Ψ = {result.psi_kl:.3f}")
print(f"D_KL = {result.d_kl:.3f}")
print(f"Normalized? {np.allclose(np.sum(result.p_current_norm), 1.0)}")
```

**Mathematical Reference**: Preprint IV, Equation (15):
```
Ψ(t) = 1 - D_KL(P_t || P_ref) / D_max
where D_max is an upper bound on plausible divergence.
```

### Viability Index (V)

```python
from acoa.metrics.viability import ViabilityIndex

# Default weights from Preprint IV
viability = ViabilityIndex()

# Or custom weights
viability = ViabilityIndex(weights={
    'uptime': 0.5,
    'error_rate': 0.3,
    'recovery_capacity': 0.2
})

# Measure viability
result = viability.measure(
    uptime=0.95,
    error_rate=0.05,
    recovery_capacity=0.8
)

print(f"V = {result.v_composite:.3f}")
print(f"Contributions: {result.contributions}")
```

**Mathematical Reference**: Preprint IV, Equation (16):
```
V(t) = w₁·uptime(t) + w₂·(1 - error(t)) + w₃·recovery(t)
```

### Antifragility Coefficient (Ω)

```python
from acoa.metrics.antifragility import AntifragilityCoefficient, StressType

# Initialize monitor
omega = AntifragilityCoefficient(min_events=5)

# Record stress events
omega.add_event(
    pre_stress_viability=0.8,
    post_stress_viability=0.9,
    stress_type=StressType.LOAD,
    stress_magnitude=0.5
)

# Compute Ω
result = omega.compute(use_bootstrap=True, categorize=True)

print(f"Ω = {result.omega:.3f}")
print(f"Gain under stress? {result.gain_under_stress}")
print(f"95% CI: {result.confidence_interval}")
print(f"By stress type: {result.omega_by_type}")
```

**Mathematical Reference**: Preprint IV, Equation (17):
```
Ω = E[V_post-stress] / E[V_pre-stress]
```

**Interpretation** (Preprint IV, Table 1):
- Ω > 1: **Antifragile** – gains from stress
- Ω = 1: **Robust** – unaffected by stress
- Ω < 1: **Fragile** – degraded by stress

## 🔬 Experimental Validation

The repository includes the A/B test protocol from **Preprint IV, Section 4**:

```bash
# Run the experimental validation
python experiments/autopoiesis_ab_test/ab_test_protocol.py

# Or use the provided script
./scripts/run_ab_test.sh
```

## 📊 Thresholds & Alerts

Default thresholds from **Preprint IV, Table 2**:

```python
THRESHOLDS = {
    'coherence': 0.85,
    'viability': 0.80,
    'antifragility': 1.0,
    'cvar': 0.30,
    'ccr': 1.0,
}

# Check thresholds
from acoa.monitoring import AlertSystem

alerts = AlertSystem(thresholds=THRESHOLDS)
alerts.check(coherence=0.82, viability=0.78)
```

## 📝 Citation

If you use ACOA in your research, please cite:

```bibtex
@article{areas2024autopoiesis,
  title={Autopoiesis Without Control: Black-Box Digital Organisms and Coherence-Based Governance via ACOA},
  author={Arêas, Gabriel},
  journal={Authorea Preprint},
  year={2024},
  doi={10.22541/au.XXXXXXX},
  url={https://www.authorea.com/doi/full/10.22541/au.XXXXXXX}
}
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Author**: Gabriel Arêas
- **ORCID**: [0009-0008-2973-4047](https://orcid.org/0009-0008-2973-4047)
- **Email**: [Your Email]
- **Preprint**: [Authorea Link](https://www.authorea.com/doi/full/10.22541/au.XXXXXXX)

## 🙏 Acknowledgments

This research builds upon:
- Maturana & Varela's theory of autopoiesis
- Taleb's antifragility framework
- Modern causal inference methods
- Digital governance literature

---

*"Governance without comprehension, coherence without control."*
*— Preprint IV Abstract*
