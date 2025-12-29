#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict

import numpy as np


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canon(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


@dataclass(frozen=True)
class ResidueV1:
    """
    Representa o resíduo canônico (oculto mensurável) gerado pelo DSBD v2.

    - symmetry_delta, entropy_increase, energy_barrier: escalares físicos/informacionais
    - residue_vector: vetor 16D determinístico derivado via SHA256 expandido
    - residue_hash: hash canônico do payload do resíduo
    """

    version: str
    symmetry_delta: float
    entropy_increase: float
    energy_barrier: float
    residue_vector: np.ndarray  # shape (16,)
    residue_hash: str  # sha256 over canonical json without itself

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "symmetry_delta": float(self.symmetry_delta),
            "entropy_increase": float(self.entropy_increase),
            "energy_barrier": float(self.energy_barrier),
            "residue_vector": [float(x) for x in self.residue_vector.tolist()],
            "residue_hash": self.residue_hash,
        }


def compute_residue_v1(
    symmetry_delta: float, entropy_increase: float, energy_barrier: float
) -> ResidueV1:
    """
    Gera resíduo canônico (16D) determinístico a partir de três escalares.
    Usa SHA256 do payload base para derivar um vetor estável em [-1, 1].
    """
    base = {
        "version": "residue.v1",
        "symmetry_delta": float(symmetry_delta),
        "entropy_increase": float(entropy_increase),
        "energy_barrier": float(energy_barrier),
    }
    h = hashlib.sha256(_canon(base)).digest()  # 32 bytes

    # Expansão determinística: 32 bytes -> 16 int16 -> normaliza para [-1, 1]
    ints = np.frombuffer(h, dtype=np.int16)  # 16 valores
    vec = ints.astype(np.float64) / 32767.0
    vec = np.clip(vec, -1.0, 1.0)

    payload = {**base, "residue_vector": [float(x) for x in vec.tolist()]}
    residue_hash = _sha256_hex(_canon(payload))

    return ResidueV1(
        version="residue.v1",
        symmetry_delta=float(symmetry_delta),
        entropy_increase=float(entropy_increase),
        energy_barrier=float(energy_barrier),
        residue_vector=vec.astype(np.float32),
        residue_hash=residue_hash,
    )
