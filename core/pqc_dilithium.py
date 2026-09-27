#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
from typing import Any, Dict, Tuple

from pqcrypto.sign import ml_dsa_65


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"), validate=True)


def _canon_bytes(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def keygen() -> Tuple[str, str]:
    """Generate ML-DSA-65 (FIPS 204; Dilithium3 lineage) keys in Base64."""
    pk, sk = ml_dsa_65.keygen()
    return _b64e(pk), _b64e(sk)


def sign(obj: Dict[str, Any], sk_b64: str) -> str:
    """Sign canonical JSON with ML-DSA-65 and return Base64 signature."""
    sk = _b64d(sk_b64)
    sig = ml_dsa_65.sign(sk, _canon_bytes(obj))
    return _b64e(sig)


def verify(obj: Dict[str, Any], sig_b64: str, pk_b64: str) -> bool:
    """Verify an ML-DSA-65 signature over canonical JSON."""
    try:
        pk = _b64d(pk_b64)
        sig = _b64d(sig_b64)
        ml_dsa_65.verify(pk, _canon_bytes(obj), sig)
        return True
    except Exception:
        return False
