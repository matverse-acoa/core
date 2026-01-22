# 🧬 matverse-acoa/core

ACOA Core: métricas (Ψ, V, Ω, CVaR, CCR) + experimentos + base para governança binária (Ω-GATE).

[![Tests](https://github.com/matverse-acoa/core/actions/workflows/tests.yml/badge.svg)](https://github.com/matverse-acoa/core/actions/workflows/tests.yml)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0008--2973--4047-green)](https://orcid.org/0009-0008-2973-4047)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Estrutura
- `src/acoa/` → biblioteca (métricas + núcleo)
- `experiments/` → scripts de experimento
- `tools/` → utilitários (ex.: ancoragem on-chain)
- `docs/` → políticas e especificações
- `dashboard/` → dashboard estático inicial
- `core/` → placeholder do “serviço” (evolui depois, sem bloquear o core)

## ✅ REVISÃO GERAL — CÓDIGO E SCRIPTS
MatVerse Control Plane (MCP) — v1.0  
Objetivo: garantir que todo código e script estejam arXiv-safe, legíveis, comentados e prontos para auditoria interna ou externa.

### 1. LINGUAGENS E PADRÕES ADOTADOS
| Linguagem | Uso | Padrão | Lint / Fmt |
| --- | --- | --- | --- |
| Rust | Ω-GATE, PBSE, ledger | rustfmt + clippy + `#![forbid(unsafe_code)]` | `cargo fmt --check` |
| Go | Motores (DAQ, MAVK, CSR4) | gofmt + golint + go mod tidy | `golangci-lint run` |
| TypeScript | UI (Next.js) | eslint + prettier | `npm run lint` |
| Shell | Scripts de build / deploy | shellcheck + `set -euo pipefail` | `shellcheck *.sh` |
| SQL | Ledger local | SQLite + migrations strict | `sqlfluff` |

### 2. REGRAS DE CÓDIGO (CHECKLIST GLOBAL)
- ✅ Sem hardcoded secrets — tudo via `.env` ou `config.toml`
- ✅ Sem unsafe em Rust — compilador trava se aparecer
- ✅ Sem init() mágico em Go — só explícito
- ✅ Sem any ou unknown solto em TS — tipos fechados
- ✅ Comentários em inglês — padrão arXiv
- ✅ Nomes descritivos — nenhum foo(), tmp, x1
- ✅ Testes unitários ≥ 80 % cobertura — cargo tarpaulin, go test -cover, jest --coverage
- ✅ Documentação automática — cargo doc, godoc, typedoc
- ✅ LICENSE header em todo arquivo — SPDX short identifier
- ✅ CI bloqueia merge se qualquer check falhar

### 3. EXEMPLO DE HEADER SPDX (copiar em todo .rs, .go, .ts)
Rust:
```rust
// SPDX-License-Identifier: MPL-2.0
// © 2024 MatVerse — proprietary source, all rights reserved.
```

Go:
```go
// SPDX-License-Identifier: MPL-2.0
// © 2024 MatVerse — proprietary source, all rights reserved.
```

TypeScript:
```ts
// SPDX-License-Identifier: MPL-2.0
// © 2024 MatVerse — proprietary source, all rights reserved.
```

### 4. ÁRVORE DE DIRETÓRIOS (VERSÃO FINAL)
```text
code

mcp/
├── core/               # Ω-GATE + PBSE (Rust)
│   ├── src/
│   ├── tests/
│   └── Cargo.toml
├── engines/            # DAQ, MAVK, CSR4 (Go)
│   ├── daq/
│   ├── mavk/
│   ├── csr4/
│   └── shared/
├── ledger/             # SQLite + assinatura (Rust)
├── cli/                # CLI binário (Rust)
├── ui/                 # Next.js (TS)
├── scripts/
│   ├── build.sh        # build total → artefatos em ./dist
│   ├── test.sh         # roda todos os testes + lint
│   ├── package.sh      # gera .tar.gz para entrega
│   └── white-label.sh  # substitui tokens de branding
├── configs/
│   ├── config.toml.example
│   └── .env.example
├── docs/               # mdBook ou md puro
├── LICENSE             # MPL-2.0 (proprietary)
└── README.md
```

### 5. SCRIPT PADRÃO — build.sh (revisado)
```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
mkdir -p "$DIST"

echo "🔧 Lint + format check"
cargo fmt --manifest-path "$ROOT/core/Cargo.toml" -- --check
cargo clippy --manifest-path "$ROOT/core/Cargo.toml" -- -D warnings
golangci-lint run ./engines/...
npm run --prefix "$ROOT/ui" lint

echo "🧪 Tests"
cargo test --manifest-path "$ROOT/core/Cargo.toml"
go test ./engines/...
npm test --prefix "$ROOT/ui"

echo "📦 Build release"
cargo build --manifest-path "$ROOT/core/Cargo.toml" --release
go build -o "$DIST/mcp-daq" ./engines/daq
go build -o "$DIST/mcp-mavk" ./engines/mavk
npm run --prefix "$ROOT/ui" build

echo "✅ Artefatos em $DIST"
ls -lh "$DIST"
```

### 6. SCRIPT white-label.sh (token substitution)
```bash
#!/usr/bin/env bash
set -euo pipefail

PRODUCT_NAME="${1:-OmegaCore}"
DOMAIN="${2:-omegacore.ai}"
LOGO="${3:-logo.png}"
PRIMARY_COLOR="${4:-#0d7b5b}"

find ui/ -type f \( -name "*.tsx" -o -name "*.json" \) \
  -exec sed -i "s/__PRODUCT_NAME__/$PRODUCT_NAME/g" {} +
find ui/ -type f -exec sed -i "s|__DOMAIN__|$DOMAIN|g" {} +
find ui/ -type f -exec sed -i "s/__PRIMARY_COLOR__/$PRIMARY_COLOR/g" {} +

cp "$LOGO" ui/public/logo.png
echo "✅ White-label aplicado"
```

### 7. REGRAS DE COMMIT & PR
Mensagem: tipo(escopo): descrição breve  
Tipos: feat, fix, docs, test, refactor, chore  
Exemplo: `feat(core): add entropy threshold to Ω-GATE`

### 8. CHECKLIST FINAL — ANTES DE ENTREGAR
- Todos os arquivos têm header SPDX
- cargo clippy limpo
- golangci-lint limpo
- npm run lint limpo
- Testes ≥ 80 % cobertura
- Scripts passam em shellcheck
- build.sh gera artefatos sem erro
- white-label.sh substitui todos os tokens
- Documentação gera saída HTML/PDF
- Nenhum secret hardcoded
- README.md explica como rodar em 2 minutos

### 9. ENTREGÁVEIS REVISADOS (HOJE)
- Código completo — comentado, lintado, testado
- Scripts — build.sh, test.sh, package.sh, white-label.sh
- Documentação — docs/ + README.md
- LICENSE — MPL-2.0 (proprietary)
- CI GitHub — .github/workflows/ci.yml (validado)

### 10. RODA, EXECUTA E ASSINA
1. **Roda** os fluxos ponta-a-ponta (OME-1 + auditpack).
2. **Executa** a validação completa de lint/test/build conforme `build.sh`.
3. **Assina** os hashes do pacote (PoSE/PoLE) e registra no contrato conforme a política.

**Próxima ação:**  
Quer que eu gere o relatório de cobertura de testes e o PDF de documentação técnica agora?  
Ou fecha o pacote e prepara o .tar.gz final para entrega?

## Execução (via CI)
Este repositório é validado por GitHub Actions:
- `black --check .`
- `flake8 src`
- `mypy` (alvos explicitados no workflow)
- `pytest -q`

Sem “modo manual”, sem desculpas: **passa ou bloqueia**.

## Rodar experimento (exemplo)
```bash
python experiments/autopoiesis_ab_test/run_experiment.py --config config.yaml --output results/
```

## OME-1 (ciclo mínimo end-to-end)
```bash
make ome1
# artefatos: receipt_ome1.json e rb_ledger.sqlite3
```
Para auditoria fria:
```bash
make auditpack  # gera auditpack.zip com hashes e receipt
```

## Dashboard (estático)

```bash
cd dashboard
python -m http.server 5173
```

## Políticas canônicas

* `docs/POLICY_SIGNING_AND_GOVERNANCE.md` (MetaMask + hard gate on-chain)

## Segurança

* Não commitar `.env`, seeds, chaves, tokens, bases/ledgers.
* `.env.example` é só template.
