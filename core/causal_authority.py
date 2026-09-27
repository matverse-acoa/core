from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, FrozenSet
import hashlib
import hmac
import json
import time


def _canon(obj: object) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


@dataclass(frozen=True)
class CausalIntent:
    principal: str
    action: str
    resource: str
    payload_hash: str


@dataclass(frozen=True)
class CapabilityLease:
    principal: str
    actions: FrozenSet[str]
    resources: FrozenSet[str]
    expires_at: int
    nonce: str


@dataclass(frozen=True)
class CausalAuthority:
    version: str
    intent: CausalIntent
    lease: CapabilityLease
    issued_at: int
    signature: str


class AuthorityError(ValueError):
    pass


class AuthorityGate:
    """Fail-closed causal authority verifier."""

    def __init__(
        self,
        sign: Callable[[bytes], str],
        verify: Callable[[bytes, str], bool],
    ):
        self._sign = sign
        self._verify = verify

    @staticmethod
    def _body(
        intent: CausalIntent, lease: CapabilityLease, issued_at: int
    ) -> dict:
        return {
            "version": "causal_authority.v1",
            "intent": {
                "principal": intent.principal,
                "action": intent.action,
                "resource": intent.resource,
                "payload_hash": intent.payload_hash,
            },
            "lease": {
                "principal": lease.principal,
                "actions": sorted(lease.actions),
                "resources": sorted(lease.resources),
                "expires_at": lease.expires_at,
                "nonce": lease.nonce,
            },
            "issued_at": issued_at,
        }

    def issue(
        self,
        intent: CausalIntent,
        lease: CapabilityLease,
        issued_at: int | None = None,
    ) -> CausalAuthority:
        issued_at = int(time.time()) if issued_at is None else int(issued_at)
        if intent.principal != lease.principal:
            raise AuthorityError("principal mismatch")
        if intent.action not in lease.actions:
            raise AuthorityError("action outside lease")
        if intent.resource not in lease.resources:
            raise AuthorityError("resource outside lease")
        if issued_at > lease.expires_at:
            raise AuthorityError("lease expired")
        body = self._body(intent, lease, issued_at)
        return CausalAuthority(
            "causal_authority.v1",
            intent,
            lease,
            issued_at,
            self._sign(_canon(body)),
        )

    def verify(
        self,
        authority: CausalAuthority,
        payload: bytes,
        now: int | None = None,
    ) -> bool:
        now = int(time.time()) if now is None else int(now)
        if authority.version != "causal_authority.v1":
            return False
        intent, lease = authority.intent, authority.lease
        if hashlib.sha256(payload).hexdigest() != intent.payload_hash:
            return False
        if intent.principal != lease.principal:
            return False
        if intent.action not in lease.actions or intent.resource not in lease.resources:
            return False
        if now > lease.expires_at or authority.issued_at > lease.expires_at:
            return False
        body = self._body(intent, lease, authority.issued_at)
        return self._verify(_canon(body), authority.signature)


class ReplayGuard:
    def __init__(self) -> None:
        self._used: set[str] = set()

    def consume(self, authority: CausalAuthority) -> bool:
        nonce = authority.lease.nonce
        if nonce in self._used:
            return False
        self._used.add(nonce)
        return True


class HMACSigner:
    """Test-only signing adapter. Not a production authority root."""

    def __init__(self, key: bytes):
        if len(key) < 32:
            raise ValueError("HMAC test key must be >=32 bytes")
        self._key = key

    def sign(self, body: bytes) -> str:
        return hmac.new(self._key, body, hashlib.sha256).hexdigest()

    def verify(self, body: bytes, signature: str) -> bool:
        return hmac.compare_digest(self.sign(body), signature)



class Dilithium3Signer:
    """Compatibility adapter backed by canonical ML-DSA-65 (FIPS 204)."""

    def __init__(self, public_key_b64: str, secret_key_b64: str | None = None):
        self._pk = public_key_b64
        self._sk = secret_key_b64

    @staticmethod
    def _object(body: bytes) -> dict:
        return {"causal_authority_canonical_b64": __import__("base64").b64encode(body).decode("ascii")}

    def sign(self, body: bytes) -> str:
        if self._sk is None:
            raise AuthorityError("secret key unavailable")
        from core.pqc_dilithium import sign

        return sign(self._object(body), self._sk)

    def verify(self, body: bytes, signature: str) -> bool:
        from core.pqc_dilithium import verify

        return verify(self._object(body), signature, self._pk)
