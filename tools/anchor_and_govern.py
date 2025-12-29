"""
Anchor governance receipts and snapshots on-chain via a minimal Polygon client.

This utility anchors three artifacts (POSE, POLE, COG) plus associated metadata
into a MATVERSE_GATE contract. It expects the following environment variables:

- POLYGON_RPC_URL: HTTP RPC endpoint (Amoy/Polygon) with baseFee support
- MATVERSE_GATE_ADDRESS: deployed gate contract address
- POLYGON_PRIVATE_KEY: private key authorized to call `anchor`

The script is intentionally dependency-light and uses a narrow ABI for the gate.
"""

from __future__ import annotations

import json
import os
from typing import Any, Tuple

import numpy as np
from eth_hash.auto import keccak
from eth_utils import to_checksum_address
from web3 import Web3
from web3.middleware import geth_poa_middleware

# ---------- helpers ----------


def canonical_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def k32(obj: Any) -> bytes:
    return keccak(canonical_json(obj))


def hex32(raw: bytes) -> str:
    if len(raw) != 32:
        raise ValueError("NOT_32_BYTES")
    return "0x" + raw.hex()


# ---------- env ----------

RPC = os.environ["POLYGON_RPC_URL"].strip()
GATE = to_checksum_address(os.environ["MATVERSE_GATE_ADDRESS"].strip())
PK = os.environ["POLYGON_PRIVATE_KEY"].strip()

w3 = Web3(Web3.HTTPProvider(RPC))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
if not w3.is_connected():
    raise SystemExit("RPC_NOT_CONNECTED")

acct = w3.eth.account.from_key(PK)

# ---------- minimal ABI ----------
ABI = [
    {
        "inputs": [
            {"internalType": "uint8", "name": "kind", "type": "uint8"},
            {"internalType": "bytes32", "name": "digest", "type": "bytes32"},
        ],
        "name": "exists",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint8", "name": "kind", "type": "uint8"},
            {"internalType": "bytes32", "name": "digest", "type": "bytes32"},
            {"internalType": "bytes32", "name": "metaHash", "type": "bytes32"},
        ],
        "name": "anchor",
        "outputs": [{"internalType": "bytes32", "name": "key", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

contract = w3.eth.contract(address=GATE, abi=ABI)

POSE, POLE, COG = 0, 1, 2


def dyn_fees() -> Tuple[int, int]:
    latest = w3.eth.get_block("latest")
    base = latest.get("baseFeePerGas", w3.to_wei(25, "gwei"))
    prio = w3.to_wei(2, "gwei")
    max_fee = int(base * 2 + prio)
    return max_fee, prio


def anchor(kind: int, digest32: bytes, meta32: bytes) -> tuple[str, int]:
    nonce = w3.eth.get_transaction_count(acct.address)
    max_fee, prio = dyn_fees()

    tx = contract.functions.anchor(kind, digest32, meta32).build_transaction(
        {
            "from": acct.address,
            "nonce": nonce,
            "chainId": w3.eth.chain_id,
            "gas": 250_000,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": prio,
        }
    )
    signed = w3.eth.account.sign_transaction(tx, PK)
    txh = w3.eth.send_raw_transaction(signed.rawTransaction)
    rcpt = w3.eth.wait_for_transaction_receipt(txh, timeout=180)
    if rcpt.status != 1:
        raise RuntimeError("ANCHOR_TX_FAILED")
    return txh.hex(), int(rcpt.blockNumber)


def ensure(kind: int, digest32: bytes, meta32: bytes) -> tuple[bool, str, int]:
    if contract.functions.exists(kind, digest32).call():
        return True, "ALREADY", 0
    txh, bn = anchor(kind, digest32, meta32)
    return False, txh, bn


# ---------- build proofs (digests) ----------
# Replace these mocks with your real metrics (Ψ/Θ/CVaR/Ω) calculations.
psi = 0.90
theta_hat = 0.86
cvar_value = 0.03
pole_valid = True

pose_receipt = {
    "artifact_sha256": "deadbeef" * 8,
    "build_id": "build-2025-12-28T00:00:00Z",
    "omega_gate_result": {
        "psi": psi,
        "theta_hat": theta_hat,
        "cvar": cvar_value,
        "pole_valid": pole_valid,
    },
    "references": {"repo": "matverse-acoa/core", "commit": "HEAD"},
}
pole_transition = {
    "prev_state_hash": "0x" + ("11" * 32),
    "next_state_hash": "0x" + ("22" * 32),
    "policy_hash": "0x" + ("33" * 32),
    "step_meta": {"k": 1, "note": "transition"},
}
cog_snapshot = {
    "G": {"goal": "ship"},
    "P": {"pipeline": "psi-theta-cvar"},
    "I": {"n": 7},
    "D": {"doc": "CONSOLIDACAO_FINAL.md"},
    "V": {"tests": "pass"},
    "A": {"deploy": "amoy"},
}

pose_d = k32(pose_receipt)
pole_d = k32(pole_transition)
cog_d = k32(cog_snapshot)

meta = k32({"manifest": "v1", "ts": "2025-12-28"})

print("POSE digest:", hex32(pose_d))
print("POLE digest:", hex32(pole_d))
print("COG  digest:", hex32(cog_d))
print("META hash  :", hex32(meta))

# ---------- anchor (Polygon = gate material) ----------
for kind, digest, name in [
    (POSE, pose_d, "POSE"),
    (POLE, pole_d, "POLE"),
    (COG, cog_d, "COG"),
]:
    existed, txh, bn = ensure(kind, digest, meta)
    if existed:
        print(name, "OK (exists)")
    else:
        print(name, "ANCHORED tx=", txh, "block=", bn)

# ---------- hard gate check ----------
ok_pose = contract.functions.exists(POSE, pose_d).call()
ok_pole = contract.functions.exists(POLE, pole_d).call()
ok_cog = contract.functions.exists(COG, cog_d).call()

print("CHAIN_PROOFS:", ok_pose, ok_pole, ok_cog)
if not (ok_pose and ok_pole and ok_cog):
    raise SystemExit("INTERDICT: CHAIN_PROOF_MISSING")

print("EXECUTE: autorizado (local + chain).")
