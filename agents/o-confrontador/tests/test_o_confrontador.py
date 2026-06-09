import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "o_confrontador.py"
POLICY = ROOT / "policies" / "confrontation_policy.json"
SCHEMA = ROOT / "schemas" / "confrontation_report.schema.json"
CLAIMS = ROOT / "examples" / "claims.json"
ARTIFACT = ROOT / "examples" / "sample_artifact"
MANIFEST = ROOT / "MANIFEST.sha256.json"

spec = importlib.util.spec_from_file_location("o_confrontador", SCRIPT)
o_confrontador = importlib.util.module_from_spec(spec)
spec.loader.exec_module(o_confrontador)


class OConfrontadorTests(unittest.TestCase):
    def test_self_confrontation_runs_and_maps_no_contest(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--artifact",
                    str(ARTIFACT),
                    "--claims",
                    str(CLAIMS),
                    "--out",
                    tmp,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report_path = Path(result.stdout.strip())
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertTrue(report["corpus_blind"])
        self.assertTrue(report["forbidden_context_rejected"])
        self.assertEqual(report["contest_level"], "NO_CONTEST")
        self.assertEqual(report["omega_gate_recommendation"], "PASS_CANDIDATE")
        self.assertEqual(report["claims_evaluated"], 1)
        self.assertEqual(report["objections"], [])

    def test_missing_evidence_holds_for_omega_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            claims_path = tmp_path / "claims.json"
            artifact_path = tmp_path / "artifact"
            artifact_path.mkdir()
            claims_path.write_text(
                json.dumps(
                    {
                        "claims": [
                            {
                                "id": "CLAIM-MISSING-EVIDENCE",
                                "statement": "This claim references unavailable evidence.",
                                "evidence": ["missing.txt"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            report = o_confrontador.confront(artifact_path, claims_path, None, POLICY)

        self.assertEqual(report["contest_level"], "MATERIAL_CONTEST")
        self.assertEqual(report["omega_gate_recommendation"], "HOLD")
        self.assertEqual(report["objections"][0]["rule"], "missing_evidence")

    def test_path_escape_blocks_for_omega_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            claims_path = tmp_path / "claims.json"
            artifact_path = tmp_path / "artifact"
            artifact_path.mkdir()
            claims_path.write_text(
                json.dumps(
                    {
                        "claims": [
                            {
                                "id": "CLAIM-PATH-ESCAPE",
                                "statement": "This claim tries to escape the artifact boundary.",
                                "evidence": ["../outside.txt"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            report = o_confrontador.confront(artifact_path, claims_path, None, POLICY)

        self.assertEqual(report["contest_level"], "FATAL_CONTEST")
        self.assertEqual(report["omega_gate_recommendation"], "BLOCK")
        self.assertEqual(report["objections"][0]["rule"], "invalid_evidence_path")

    def test_policy_contains_complete_omega_mapping(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertTrue(policy["corpus_blind"])
        self.assertEqual(
            policy["omega_gate_mapping"],
            {
                "NO_CONTEST": "PASS_CANDIDATE",
                "WEAK_CONTEST": "PASS_WITH_NOTES",
                "MATERIAL_CONTEST": "HOLD",
                "FATAL_CONTEST": "BLOCK",
            },
        )

    def test_schema_declares_required_output_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        required = set(schema["required"])
        self.assertIn("contest_level", required)
        self.assertIn("omega_gate_recommendation", required)
        self.assertIn("input_manifest", required)
        self.assertEqual(schema["properties"]["corpus_blind"]["const"], True)
        self.assertFalse(schema["additionalProperties"])


    def test_sample_report_matches_schema_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        report = o_confrontador.confront(ARTIFACT, CLAIMS, None, POLICY)

        self.assertEqual(set(report), set(schema["properties"]))
        for field in schema["required"]:
            self.assertIn(field, report)
        self.assertEqual(report["agent"], schema["properties"]["agent"]["const"])
        self.assertEqual(report["codename"], schema["properties"]["codename"]["const"])
        self.assertTrue(report["corpus_blind"])
        self.assertTrue(report["forbidden_context_rejected"])
        self.assertIn(report["contest_level"], schema["properties"]["contest_level"]["enum"])
        self.assertIn(
            report["omega_gate_recommendation"],
            schema["properties"]["omega_gate_recommendation"]["enum"],
        )
        self.assertRegex(report["input_manifest"]["claims"], r"^[a-f0-9]{64}$")
        for file_hashes in (report["input_manifest"]["artifact"], report["input_manifest"]["evidence_pack"]):
            for digest in file_hashes.values():
                self.assertRegex(digest, r"^[a-f0-9]{64}$")

    def test_manifest_sha256_valid(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for relative_path, expected in manifest["files"].items():
            file_path = ROOT / relative_path
            digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
            self.assertEqual(digest, expected, relative_path)


if __name__ == "__main__":
    unittest.main()
