"""Atlas — constituição, invariantes, leis, cartografia de linhagem.

Resolução da colisão ACOA/Atlas (MATVERSE 2.0, §4 — mesma patologia de twin
que obra vs. pessoa: um nome carregando funções incompatíveis):

    Atlas   → constituição, invariantes, leis, cartografia de linhagem
    ACOA    → coerência, autopoiese, antifragilidade, auditoria
            → capacidade transversal, NÃO órgão constitucional

`atlas` é onde as invariantes vivem. `acoa` (o pacote irmão, já
implementado neste repositório: `acoa.core`, `acoa.metrics`) é a
capacidade que essas invariantes governam — não o contrário.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import product
from typing import Dict, Tuple


class Organism(Enum):
    """Separação funcional: que tipo de saída um resultado produz."""

    SCIENCE = "science"
    ENGINEERING = "engineering"
    CAPITALS = "capitals"


class Domain(Enum):
    """Soberania de autoridade: quem tem autoridade para validar."""

    HUMAN = "human"
    COMPUTATIONAL = "computational"


@dataclass(frozen=True)
class Invariant:
    code: str
    statement: str
    group: str


INVARIANTS: Dict[str, Invariant] = {
    inv.code: inv
    for inv in (
        # Capitais
        Invariant("I-C1", "capital não compra admissibilidade", "capitals"),
        Invariant("I-C2", "admissibilidade não garante retorno", "capitals"),
        Invariant("I-C3", "Capitals lê o estado científico, nunca escreve", "capitals"),
        # Twin
        Invariant("I-T1", "histórico preservado", "twin"),
        Invariant("I-T2", "extensão preservada", "twin"),
        Invariant("I-T3", "inferência marcada", "twin"),
        Invariant("I-T4", "autoria de quem produziu", "twin"),
        Invariant("I-T5", "nunca primeira pessoa pelo autor", "twin"),
        Invariant("I-T6", "nunca endosso contrafactual", "twin"),
        # Federação
        Invariant(
            "I-F1", "autoridade arquitetural ≠ autoridade de domínio", "federation"
        ),
        Invariant("I-F2", "síntese de IA não conta como validação", "federation"),
        Invariant("I-F3", "repetição não gera T_I", "federation"),
        Invariant(
            "I-F4", "convergência preserva a divergência no registro", "federation"
        ),
    )
}

NO_FOURTH_ORGANISM = "não existe quarto organismo"


def check(code: str) -> Invariant:
    """Recupera uma invariante pelo código; falha alto se desconhecida."""
    if code not in INVARIANTS:
        raise KeyError(f"invariante desconhecida: {code}")
    return INVARIANTS[code]


def invariants_by_group(group: str) -> Tuple[Invariant, ...]:
    return tuple(inv for inv in INVARIANTS.values() if inv.group == group)


def organism_domain_matrix() -> Dict[Tuple[Organism, Domain], None]:
    """Organismo × domínio: eixos ortogonais que compõem, não colidem."""
    return {pair: None for pair in product(Organism, Domain)}
