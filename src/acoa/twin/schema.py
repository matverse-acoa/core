"""Schema genérico do Twin: ⟨X₀, 𝒯, I, Λ, X_t⟩.

O Twin é o objeto que atravessa os três organismos (Science, Engineering,
Capitals) sem pertencer a nenhum. Oito instâncias compartilham o mesmo
schema: Work, Model, Dataset, Algorithm, System, Policy, Artifact, Document.

    X₀  estado inicial (fonte primária)
    𝒯   sequência ordenada de transformações
    I   invariantes que a travessia deve preservar
    Λ   relação de linhagem: qual estado é a fonte primária
    X_t estado atual (representação vinculada a X₀ via 𝒯)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class TwinInstance(Enum):
    WORK = "work"
    MODEL = "model"
    DATASET = "dataset"
    ALGORITHM = "algorithm"
    SYSTEM = "system"
    POLICY = "policy"
    ARTIFACT = "artifact"
    DOCUMENT = "document"


class TwinState(Enum):
    """Paper → Twin → Artifact → Asset (ordem não regressiva)."""

    PAPER = "paper"
    TWIN = "twin"
    ARTIFACT = "artifact"
    ASSET = "asset"


@dataclass(frozen=True)
class Transformation:
    label: str
    actor: str


@dataclass
class Twin:
    instance: TwinInstance
    x0: Any
    lineage_primary: str = "x0"
    state: TwinState = TwinState.TWIN
    transformations: List[Transformation] = field(default_factory=list)
    invariants: Dict[str, bool] = field(default_factory=dict)
    xt: Any = None

    def __post_init__(self) -> None:
        if self.xt is None:
            self.xt = self.x0

    def apply(self, label: str, actor: str, result: Any) -> None:
        """Registra uma transformação em 𝒯 e atualiza X_t."""
        self.transformations.append(Transformation(label, actor))
        self.xt = result

    def advance(self, state: TwinState) -> None:
        """Move o Twin ao longo de Paper → Twin → Artifact → Asset.

        Nunca regride: cada estado é uma promoção, não uma edição.
        """
        order = list(TwinState)
        if order.index(state) < order.index(self.state):
            raise ValueError(
                f"twin não pode regredir de {self.state.value} para {state.value}"
            )
        self.state = state

    def check_invariant(self, name: str, holds: bool) -> None:
        self.invariants[name] = holds

    @property
    def preserved(self) -> bool:
        """True se toda invariante checada até agora se sustenta (I)."""
        return all(self.invariants.values()) if self.invariants else True
