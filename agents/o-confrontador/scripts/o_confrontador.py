#!/usr/bin/env python3
"""Corpus-blind adversarial confrontation for MatVerse ACOA Core."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SEVERITY_ORDER = {
    "NO_CONTEST": 0,
    "WEAK_CONTEST": 1,
    "MATERIAL_CONTEST": 2,
    "FATAL_CONTEST": 3,
}

DEFAULT_POLICY = Path(__file__).resolve().parents[1] / "policies" / "confrontation_policy.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def safe_relative_path(root: Path, candidate: str) -> Path | None:
    if not candidate or Path(candidate).is_absolute():
        return None
    resolved_root = root.resolve()
    resolved_candidate = (resolved_root / candidate).resolve()
    if resolved_candidate == resolved_root or resolved_root in resolved_candidate.parents:
        return resolved_candidate
    return None


def collect_hashes(root: Path | None) -> dict[str, str]:
    if root is None or not root.exists():
        return {}
    if root.is_file():
        return {root.name: sha256_file(root)}
    hashes: dict[str, str] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        hashes[path.relative_to(root).as_posix()] = sha256_file(path)
    return hashes


def read_text_lossy(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def add_objection(
    objections: list[dict[str, str]],
    claim_id: str,
    rule: str,
    severity: str,
    message: str,
    path: str | None = None,
) -> None:
    objection = {
        "claim_id": claim_id,
        "rule": rule,
        "severity": severity,
        "message": message,
    }
    if path is not None:
        objection["path"] = path
    objections.append(objection)


def max_contest_level(objections: list[dict[str, str]]) -> str:
    if not objections:
        return "NO_CONTEST"
    return max((item["severity"] for item in objections), key=lambda level: SEVERITY_ORDER[level])


def normalize_claims(raw_claims: Any) -> list[dict[str, Any]]:
    if isinstance(raw_claims, dict) and isinstance(raw_claims.get("claims"), list):
        return raw_claims["claims"]
    if isinstance(raw_claims, list):
        return raw_claims
    return []


def compile_patterns(patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(pattern) for pattern in patterns]


def confront(
    artifact: Path,
    claims_path: Path,
    evidence_pack: Path | None,
    policy_path: Path,
) -> dict[str, Any]:
    policy = load_json(policy_path)
    raw_claims = load_json(claims_path)
    claims = normalize_claims(raw_claims)
    objections: list[dict[str, str]] = []

    sensitive_patterns = compile_patterns(policy["sensitive_patterns"])
    contradiction_markers = policy["contradiction_markers"]
    absolute_terms = [term.lower() for term in policy["absolute_language_terms"]]

    if not claims:
        add_objection(
            objections,
            "GLOBAL",
            "missing_claim_statement",
            policy["rules"]["missing_claim_statement"],
            "claims.json must contain a non-empty claims array.",
            claims_path.as_posix(),
        )

    all_scan_roots = [artifact, claims_path]
    if evidence_pack is not None:
        all_scan_roots.append(evidence_pack)

    for root in all_scan_roots:
        files = [root] if root.is_file() else [item for item in root.rglob("*") if item.is_file()]
        for file_path in files:
            try:
                text = read_text_lossy(file_path)
            except OSError:
                add_objection(
                    objections,
                    "GLOBAL",
                    "unreadable_evidence",
                    policy["rules"]["unreadable_evidence"],
                    "Input file could not be read during confrontation.",
                    file_path.as_posix(),
                )
                continue
            for pattern in sensitive_patterns:
                if pattern.search(text):
                    add_objection(
                        objections,
                        "GLOBAL",
                        "sensitive_token_exposure",
                        policy["rules"]["sensitive_token_exposure"],
                        "Potential sensitive token exposure detected in allowed input.",
                        file_path.as_posix(),
                    )
            for marker in contradiction_markers:
                if marker in text:
                    add_objection(
                        objections,
                        "GLOBAL",
                        "contradiction_marker",
                        policy["rules"]["contradiction_marker"],
                        f"Contradiction marker detected: {marker}",
                        file_path.as_posix(),
                    )

    for index, claim in enumerate(claims):
        claim_id = str(claim.get("id") or f"CLAIM_INDEX_{index}") if isinstance(claim, dict) else f"CLAIM_INDEX_{index}"
        if not isinstance(claim, dict):
            add_objection(
                objections,
                claim_id,
                "missing_claim_statement",
                policy["rules"]["missing_claim_statement"],
                "Claim entry must be an object.",
            )
            continue

        statement = str(claim.get("statement") or "").strip()
        if not claim.get("id"):
            add_objection(
                objections,
                claim_id,
                "missing_claim_id",
                policy["rules"]["missing_claim_id"],
                "Claim is missing a stable id.",
            )
        if not statement:
            add_objection(
                objections,
                claim_id,
                "missing_claim_statement",
                policy["rules"]["missing_claim_statement"],
                "Claim is missing a statement.",
            )

        evidence = claim.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            add_objection(
                objections,
                claim_id,
                "missing_evidence",
                policy["rules"]["missing_evidence"],
                "Claim has no evidence references.",
            )
            evidence = []

        statement_lower = statement.lower()
        if any(term in statement_lower for term in absolute_terms):
            add_objection(
                objections,
                claim_id,
                "absolute_language_without_scope",
                policy["rules"]["absolute_language_without_scope"],
                "Claim uses absolute language that should be scoped before promotion.",
            )

        for reference in evidence:
            if not isinstance(reference, str):
                add_objection(
                    objections,
                    claim_id,
                    "invalid_evidence_path",
                    policy["rules"]["invalid_evidence_path"],
                    "Evidence reference must be a relative string path.",
                )
                continue
            candidate = safe_relative_path(artifact, reference)
            if candidate is None:
                add_objection(
                    objections,
                    claim_id,
                    "invalid_evidence_path",
                    policy["rules"]["invalid_evidence_path"],
                    "Evidence reference escapes the artifact boundary or is absolute.",
                    reference,
                )
                continue
            if not candidate.exists() and evidence_pack is not None:
                candidate = safe_relative_path(evidence_pack, reference)
            if candidate is None or not candidate.exists() or not candidate.is_file():
                add_objection(
                    objections,
                    claim_id,
                    "missing_evidence",
                    policy["rules"]["missing_evidence"],
                    "Evidence reference does not resolve to a supplied file.",
                    reference,
                )

    contest_level = max_contest_level(objections)
    return {
        "agent": policy["agent"],
        "codename": policy["codename"],
        "policy_id": policy["policy_id"],
        "corpus_blind": bool(policy["corpus_blind"]),
        "forbidden_context_rejected": True,
        "contest_level": contest_level,
        "omega_gate_recommendation": policy["omega_gate_mapping"][contest_level],
        "claims_evaluated": len(claims),
        "objections": objections,
        "input_manifest": {
            "artifact": collect_hashes(artifact),
            "claims": sha256_file(claims_path),
            "evidence_pack": collect_hashes(evidence_pack),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run O_CONFRONTADOR corpus-blind confrontation.")
    parser.add_argument("--artifact", required=True, type=Path, help="Allowed artifact directory.")
    parser.add_argument("--claims", required=True, type=Path, help="Allowed claims.json file.")
    parser.add_argument("--evidence-pack", type=Path, default=None, help="Optional allowed evidence pack directory.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY, help="Confrontation policy JSON.")
    parser.add_argument("--out", required=True, type=Path, help="Output directory for confrontation_report.json.")
    args = parser.parse_args()

    report = confront(args.artifact, args.claims, args.evidence_pack, args.policy)
    args.out.mkdir(parents=True, exist_ok=True)
    report_path = args.out / "confrontation_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
