from dataclasses import replace
import hashlib
import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "core" / "causal_authority.py"
SPEC = importlib.util.spec_from_file_location("causal_authority", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
causal_authority = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(causal_authority)

AuthorityGate = causal_authority.AuthorityGate
CapabilityLease = causal_authority.CapabilityLease
CausalIntent = causal_authority.CausalIntent
HMACSigner = causal_authority.HMACSigner
ReplayGuard = causal_authority.ReplayGuard


class CausalAuthorityTests(unittest.TestCase):
    def setUp(self):
        signer = HMACSigner(b"x" * 32)
        self.gate = AuthorityGate(signer.sign, signer.verify)
        self.payload = b"query=state"
        self.intent = CausalIntent(
            "cassandra",
            "READ",
            "atlas:/public",
            hashlib.sha256(self.payload).hexdigest(),
        )
        self.lease = CapabilityLease(
            "cassandra",
            frozenset({"READ"}),
            frozenset({"atlas:/public"}),
            2000,
            "n-1",
        )
        self.auth = self.gate.issue(self.intent, self.lease, issued_at=1000)

    def test_authorized(self):
        self.assertTrue(self.gate.verify(self.auth, self.payload, now=1500))

    def test_action_escalation_blocked(self):
        bad = replace(self.auth, intent=replace(self.intent, action="WRITE"))
        self.assertFalse(self.gate.verify(bad, self.payload, now=1500))

    def test_resource_escape_blocked(self):
        bad = replace(
            self.auth,
            intent=replace(self.intent, resource="secrets:/root"),
        )
        self.assertFalse(self.gate.verify(bad, self.payload, now=1500))

    def test_principal_substitution_blocked(self):
        bad = replace(
            self.auth,
            intent=replace(self.intent, principal="executor"),
        )
        self.assertFalse(self.gate.verify(bad, self.payload, now=1500))

    def test_payload_tamper_blocked(self):
        self.assertFalse(
            self.gate.verify(self.auth, b"query=state&write=true", now=1500)
        )

    def test_signature_forgery_blocked(self):
        bad = replace(self.auth, signature="00" * 32)
        self.assertFalse(self.gate.verify(bad, self.payload, now=1500))

    def test_expiry_blocked(self):
        self.assertFalse(self.gate.verify(self.auth, self.payload, now=2001))

    def test_lease_mutation_blocked(self):
        bad_lease = replace(
            self.lease,
            actions=frozenset({"READ", "WRITE"}),
        )
        bad = replace(self.auth, lease=bad_lease)
        self.assertFalse(self.gate.verify(bad, self.payload, now=1500))

    def test_replay_guard(self):
        guard = ReplayGuard()
        self.assertTrue(guard.consume(self.auth))
        self.assertFalse(guard.consume(self.auth))


if __name__ == "__main__":
    unittest.main()
