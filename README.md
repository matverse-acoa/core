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
