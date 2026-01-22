#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="${REPO_ROOT}/.githooks"

git config core.hooksPath "${HOOKS_DIR}"

chmod +x "${HOOKS_DIR}/pre-commit" "${HOOKS_DIR}/commit-msg"

cat <<'EOF'
✅ Hooks instalados. Para ativar assinatura:
1) Gere a chave SSH e salve em .git/matverse/commit_signing_ed25519(.pub)
2) Configure o Git para assinatura SSH (gpg.format ssh)
3) Faça commit normalmente; o receipt será gerado automaticamente.
EOF
