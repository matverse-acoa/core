"""Carrega e valida o registry `configs/allocation.json`.

allocation.json: organism × domain × sphere × maturity × status

Uma entrada nasce ambígua se `organism`/`domain` apontam para um valor fora
do eixo Organism/Domain, ou se `status` não é um dos estados reconhecidos.
Entradas transversais (ex.: atlas, acoa) declaram organism/domain como
null — elas não pertencem a uma célula da matriz, atravessam todas.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .constitution import Domain, Organism

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "configs" / "allocation.json"

VALID_STATUSES = {
    "implemented",
    "external",
    "closed_not_implemented",
    "measured_delta_i_zero_cost_unmeasured",
}


@dataclass(frozen=True)
class AllocationEntry:
    id: str
    organism: Optional[Organism]
    domain: Optional[Domain]
    sphere: str
    maturity: str
    status: str
    note: str = ""


@dataclass(frozen=True)
class Allocation:
    version: str
    entries: Tuple[AllocationEntry, ...]

    def get(self, entry_id: str) -> AllocationEntry:
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        raise KeyError(f"allocation desconhecida: {entry_id}")

    def by_organism(self, organism: Organism) -> Tuple[AllocationEntry, ...]:
        return tuple(e for e in self.entries if e.organism is organism)


def load_allocation(path: Path = DEFAULT_PATH) -> Allocation:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    entries: List[AllocationEntry] = []
    seen_ids: set = set()

    for raw_entry in raw["entries"]:
        entry_id = raw_entry["id"]
        if entry_id in seen_ids:
            raise ValueError(f"allocation.json: id duplicado '{entry_id}'")
        seen_ids.add(entry_id)

        organism = (
            Organism(raw_entry["organism"]) if raw_entry.get("organism") else None
        )
        domain = Domain(raw_entry["domain"]) if raw_entry.get("domain") else None

        status = raw_entry["status"]
        if status not in VALID_STATUSES:
            raise ValueError(
                f"allocation.json: status desconhecido '{status}' em '{entry_id}'"
            )

        entries.append(
            AllocationEntry(
                id=entry_id,
                organism=organism,
                domain=domain,
                sphere=raw_entry["sphere"],
                maturity=raw_entry["maturity"],
                status=status,
                note=raw_entry.get("note", ""),
            )
        )

    return Allocation(version=raw["version"], entries=tuple(entries))
