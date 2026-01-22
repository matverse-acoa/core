#!/usr/bin/env python3
import json
from pathlib import Path


def main() -> None:
    receipts_dir = Path("audit/receipts")
    receipts = sorted(receipts_dir.glob("*.json"))
    decision = "PASS" if receipts else "FAIL"

    result = {
        "schema": "matverse.pbse.guard.v1",
        "decision": decision,
        "receipts_found": len(receipts),
    }

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
