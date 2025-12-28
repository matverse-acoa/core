"""
UMJAM-Ω core entrypoint.

This placeholder wires the monorepo layout while keeping the existing ACOA
modules untouched. Extend this file with the CASSANDRA cycle (R1–R4), Ω-GATE
logic, ledger append-only services, and any supporting infrastructure
adapters under ``core/governance``, ``core/interfaces``, ``core/infrastructure``
and ``core/umjam``.
"""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    """Basic bootstrap placeholder for the UMJAM-Ω core."""

    project_root = Path(__file__).resolve().parents[1]
    print("UMJAM-Ω core ready.")
    print(f"Project root: {project_root}")
    print("Add your CASSANDRA and Ω-GATE pipelines here.")


if __name__ == "__main__":
    main()
