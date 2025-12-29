#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${ROOT}/_auditpack"
rm -rf "$OUT"
mkdir -p "$OUT"

# 1) contexto de ambiente
python -V > "$OUT/python_version.txt" || true
pip freeze > "$OUT/pip_freeze.txt" || true

# 2) ciclo OME-1
cd "$ROOT"
make ome1

# 3) coleta de artefatos
cp -f receipt_ome1.json "$OUT/" 2>/dev/null || true
cp -f rb_ledger.sqlite3 "$OUT/" 2>/dev/null || true

# 4) hashes
python - <<'PY'
import hashlib, json, os

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

out = "_auditpack"
items = {}
for fn in ["receipt_ome1.json", "rb_ledger.sqlite3"]:
    path = os.path.join(out, fn)
    if os.path.exists(path):
        items[fn] = sha256_file(path)

with open(os.path.join(out, "hashes.json"), "w", encoding="utf-8") as fh:
    json.dump(items, fh, sort_keys=True, indent=2)
print("hashes:", items)
PY

# 5) pacote final
cd "$ROOT"
zip -r auditpack.zip _auditpack >/dev/null
echo "OK: auditpack.zip gerado"
# cópia opcional para verificação local fora do zip
cp -f _auditpack/hashes.json hashes.json 2>/dev/null || true
