#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def git_root() -> Path:
    return Path(run(["git", "rev-parse", "--show-toplevel"]))


def staged_patch() -> str:
    return subprocess.check_output(["git", "diff", "--cached", "--binary"], text=True)


def sha3_256(data: str) -> str:
    return hashlib.sha3_256(data.encode("utf-8", errors="surrogatepass")).hexdigest()


def main() -> None:
    root = git_root()
    repo_name = root.name
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    head = run(["git", "rev-parse", "HEAD"])
    ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    patch_hash = sha3_256(staged_patch())
    receipt_id = f"{ts_utc.replace(':', '').replace('-', '').replace('Z', '')}_{repo_name}_{branch}_{patch_hash[:16]}"

    receipt = {
        "schema": "matverse.pbse.receipt.v1",
        "ts_utc": ts_utc,
        "repo_root": str(root),
        "repo_name": repo_name,
        "branch": branch,
        "author": {
            "name": os.environ.get("GIT_AUTHOR_NAME")
            or run(["git", "config", "user.name"]),
            "email": os.environ.get("GIT_AUTHOR_EMAIL")
            or run(["git", "config", "user.email"]),
        },
        "git": {
            "head": head,
            "index_patch_sha3_256": patch_hash,
        },
        "receipt_id": receipt_id,
    }

    audit_dir = root / "audit" / "receipts"
    audit_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = audit_dir / f"{receipt_id}.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
