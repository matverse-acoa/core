#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
from typing import Any, Dict, Tuple

from pqcrypto.sign import dilithium3


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def _canon_bytes(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def keygen() -> Tuple[str, str]:
    """Gera par de chaves Dilithium3 (pk, sk) em Base64."""
    pk, sk = dilithium3.generate_keypair()
    return _b64e(pk), _b64e(sk)


def sign(obj: Dict[str, Any], sk_b64: str) -> str:
    """Assina o payload canônico (JSON ordenado) com Dilithium3, retorna Base64."""
    sk = _b64d(sk_b64)
    sig = dilithium3.sign(_canon_bytes(obj), sk)
    return _b64e(sig)


def verify(obj: Dict[str, Any], sig_b64: str, pk_b64: str) -> bool:
    """Verifica assinatura Dilithium3 (payload canônico)."""
    pk = _b64d(pk_b64)
    sig = _b64d(sig_b64)
    try:
        dilithium3.verify(sig, _canon_bytes(obj), pk)
        return True
    except Exception:
        return False
