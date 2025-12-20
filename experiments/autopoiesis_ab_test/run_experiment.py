"""Executador de experimentos simplificado seguindo as especificações."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "src"))

from acoa.core.autopoiesis import AutopoieticCore, SystemState
from acoa.metrics.cvar import CVaREstimator


@dataclass
class ExperimentConfig:
    seed: int = 199917401948
    n_events: int = 1000
    pareto_alpha: float = 1.5
    extreme_probability: float = 0.01
    extreme_multiplier: float = 10.0
    state_dimension: int = 100
    min_ccr: float = 1.0
    min_omega: float = 1.0
    max_cvar: float = 0.30
    min_psi: float = 0.85
    min_viability: float = 0.80


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--output", default="results/")
    args = parser.parse_args()

    cfg = ExperimentConfig()
    if Path(args.config).exists():
        with open(args.config, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            cfg = ExperimentConfig(**data)

    np.random.seed(cfg.seed)

    state = np.random.randn(cfg.state_dimension)
    ccr = AutopoieticCore()
    cvar = CVaREstimator(alpha=0.95)
    timeline = []

    for i in range(cfg.n_events):
        stress = np.random.pareto(cfg.pareto_alpha)
        external = np.array([stress])
        new_state = state + 1.5 * state + 0.3 * stress * np.random.randn(cfg.state_dimension)
        st = SystemState(internal=state, external=external, output=new_state, timestamp=float(i))
        meas = ccr.measure_ccr(st)
        loss = float(np.linalg.norm(new_state - state))
        cvar.update(loss)
        timeline.append({"event": i, "ccr": meas.ccr, "loss": loss})
        state = new_state

    result = {
        "config": asdict(cfg),
        "ccr_mean": ccr.get_statistics()["mean_ccr"],
        "p_autopoietic": ccr.get_statistics()["p_autopoietic"],
        "cvar": cvar.compute().cvar,
    }

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print("Experiment finished. Summary saved to", outdir / "summary.json")


if __name__ == "__main__":
    main()
