"""Harness de três braços: mede C_K para travessias de Twin.

Braço 1: ome1_traversal      Engineering ∩ Computational, n=1
                             Ω-Gate PASS, replay EXACT_MATCH, ΔI=0 medido;
                             custo vem de instrumentação real (ex.:
                             receipt_ome1.json), nunca inferido aqui.
Braço 2: document_twin       Science ∩ Human, T_I > 0 quando federado
Braço 3: synthetic_baseline  piso de custo: travessia trivial, sem I/O

Um braço com n=1 não é harness — é anedota. Os três juntos são o mínimo
para comparar C_K entre organismos/domínios distintos.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict

from acoa.twin.document_twin import DocumentTwin


@dataclass(frozen=True)
class ArmResult:
    arm: str
    cost_seconds: float
    delta_i: float
    t_independence: float


class BenchHarness:
    def __init__(self) -> None:
        self._arms: Dict[str, Callable[[], ArmResult]] = {}

    def register(self, name: str, runner: Callable[[], ArmResult]) -> None:
        self._arms[name] = runner

    def run(self, name: str) -> ArmResult:
        if name not in self._arms:
            raise KeyError(f"braço desconhecido: {name}")
        return self._arms[name]()

    def run_all(self) -> Dict[str, ArmResult]:
        return {name: runner() for name, runner in self._arms.items()}


def synthetic_baseline_arm() -> ArmResult:
    """Piso de custo: nenhuma transformação, nenhuma travessia de fronteira."""
    t0 = time.time()
    t1 = time.time()
    return ArmResult("synthetic_baseline", t1 - t0, delta_i=0.0, t_independence=0.0)


def document_twin_arm(twin: DocumentTwin) -> ArmResult:
    """ΔI aqui é a divergência que o autor reportou, não uma métrica de KL."""
    return ArmResult(
        "document_twin",
        cost_seconds=twin.cost,
        delta_i=0.0 if twin.confirmed else 1.0,
        t_independence=twin.t_independence,
    )


def ome1_traversal_arm(cost_seconds: float) -> ArmResult:
    """Braço com n=1: Ω-Gate PASS, replay EXACT_MATCH, ΔI=0 medido.

    `cost_seconds` deve vir de instrumentação real do ciclo OME-1, não ser
    fabricado — é exatamente o dado que falta hoje ao corpus.
    """
    return ArmResult("ome1_traversal", cost_seconds, delta_i=0.0, t_independence=0.0)
