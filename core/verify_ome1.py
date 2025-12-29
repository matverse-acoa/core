#!/usr/bin/env python3
"""
Validação fria do ciclo OME-1:
- Confere hashes declarados em hashes.json
- Verifica assinatura PQC (Dilithium3) do payload canônico
- Recalcula residue.v1 hash
- Confere ledger_head (sha256 do rb_ledger.sqlite3)
"""
import base64
import hashlib
import json
import os
import sys
from typing import Any, Dict, Tuple

try:
    from pqcrypto.sign import dilithium3
except Exception as exc:  # pragma: no cover
    print(
        "ERROR: pqcrypto not installed. Run: python -m pip install pqcrypto",
        file=sys.stderr,
    )
    raise

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RECEIPT = os.path.join(ROOT, "receipt_ome1.json")
LEDGER = os.path.join(ROOT, "rb_ledger.sqlite3")
HASHES = os.path.join(ROOT, "_auditpack", "hashes.json")
HASHES_FALLBACK = os.path.join(ROOT, "hashes.json")


def die(msg: str, code: int = 2) -> None:
    print(f"VERIFY_FAIL: {msg}", file=sys.stderr)
    sys.exit(code)


def ok(msg: str) -> None:
    print(f"OK: {msg}")


def read_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        die(f"missing file: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canon_bytes(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def verify_dilithium3(payload: Dict[str, Any], sig_b64: str, pk_b64: str) -> bool:
    sig = b64d(sig_b64)
    pk = b64d(pk_b64)
    try:
        dilithium3.verify(sig, canon_bytes(payload), pk)
        return True
    except Exception:
        return False


def compute_residue_hash(residue: Dict[str, Any]) -> str:
    required = [
        "version",
        "symmetry_delta",
        "entropy_increase",
        "energy_barrier",
        "residue_vector",
    ]
    for key in required:
        if key not in residue:
            die(f"residue missing key: {key}")

    payload = {
        "version": residue["version"],
        "symmetry_delta": float(residue["symmetry_delta"]),
        "entropy_increase": float(residue["entropy_increase"]),
        "energy_barrier": float(residue["energy_barrier"]),
        "residue_vector": [float(x) for x in residue["residue_vector"]],
    }
    return hashlib.sha256(canon_bytes(payload)).hexdigest()


def extract_pose(receipt: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Aceita dois formatos:
    A) receipt["pose"] = {..., "signatures": {...}}
    B) receipt é o pose direto
    """
    pose = (
        receipt["pose"]
        if "pose" in receipt and isinstance(receipt["pose"], dict)
        else receipt
    )
    if "signatures" not in pose or not isinstance(pose["signatures"], dict):
        die("missing signatures block in pose/receipt")
    signatures = pose["signatures"]
    payload = {k: v for k, v in pose.items() if k != "signatures"}
    return payload, signatures


def main() -> None:
    if not os.path.exists(RECEIPT):
        die("receipt_ome1.json not found (expected at repo root)")
    if not os.path.exists(LEDGER):
        die("rb_ledger.sqlite3 not found (expected at repo root)")

    hashes_path = HASHES if os.path.exists(HASHES) else HASHES_FALLBACK
    if not os.path.exists(hashes_path):
        die("hashes.json not found (run make auditpack or place hashes.json)")
    hashes = read_json(hashes_path)

    # valida hashes
    for fn, expected in hashes.items():
        candidates = [
            os.path.join(ROOT, fn),
            os.path.join(ROOT, "_auditpack", fn),
        ]
        full = next((c for c in candidates if os.path.exists(c)), None)
        if not full:
            die(f"hashes.json references missing file: {fn}")
        got = sha256_file(full)
        if got != expected:
            die(f"sha256 mismatch for {fn}: expected {expected}, got {got}")
        ok(f"sha256 OK for {fn}")

    receipt = read_json(RECEIPT)
    payload, signatures = extract_pose(receipt)
    payload_for_sig = dict(payload)
    payload_for_sig.pop("ledger_head", None)

    # PQC
    pqc = signatures.get("pqc")
    if not isinstance(pqc, dict):
        die("missing signatures.pqc dict")
    alg = pqc.get("alg")
    pk_b64 = pqc.get("pk")
    sig_b64 = pqc.get("sig")
    if alg != "Dilithium3":
        die(f"unexpected PQC alg: {alg} (expected Dilithium3)")
    if not isinstance(pk_b64, str) or not isinstance(sig_b64, str):
        die("signatures.pqc.pk and signatures.pqc.sig must be base64 strings")
    if not verify_dilithium3(payload_for_sig, sig_b64, pk_b64):
        die("PQC Dilithium3 signature verification FAILED")
    ok("PQC Dilithium3 signature OK")

    # residue
    if "residue" not in payload or not isinstance(payload["residue"], dict):
        die("payload missing residue (expected residue.v1)")
    residue = payload["residue"]
    expected_residue = residue.get("residue_hash")
    if not isinstance(expected_residue, str):
        die("payload.residue.residue_hash must be string")
    computed_residue = compute_residue_hash(residue)
    if computed_residue != expected_residue:
        die(
            "residue_hash mismatch: "
            f"expected {expected_residue}, got {computed_residue}"
        )
    ok("residue.v1 hash OK")

    # ledger_head
    ledger_head = payload.get("ledger_head")
    if not isinstance(ledger_head, str):
        die("payload missing ledger_head (expected sha256 of rb_ledger.sqlite3)")
    ledger_sha = sha256_file(LEDGER)
    if ledger_sha != ledger_head:
        die(f"ledger_head mismatch: expected {ledger_head}, got {ledger_sha}")
    ok("ledger_head OK")

    ok("OME-1 VERIFY PASSED (hashes + PQC + residue + ledger_head)")


if __name__ == "__main__":
    main()
