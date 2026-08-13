"""Atlas — camada constitucional do MatVerse."""

from .constitution import (
    INVARIANTS,
    NO_FOURTH_ORGANISM,
    Domain,
    Invariant,
    Organism,
    check,
    organism_domain_matrix,
)
from .allocation import Allocation, AllocationEntry, load_allocation

__all__ = [
    "INVARIANTS",
    "NO_FOURTH_ORGANISM",
    "Domain",
    "Invariant",
    "Organism",
    "check",
    "organism_domain_matrix",
    "Allocation",
    "AllocationEntry",
    "load_allocation",
]
