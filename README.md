# 🧬 matverse-acoa/core

[![Tests](https://github.com/matverse-acoa/core/actions/workflows/tests.yml/badge.svg)](https://github.com/matverse-acoa/core/actions/workflows/tests.yml)

Repositório do **ACOA Core**: métricas (Ψ, V, Ω, CVaR, CCR) + experimentos + base para um serviço de governança (Ω-GATE).

## Estrutura
- `src/acoa/` → biblioteca de métricas e utilitários
- `experiments/` → scripts de experimento
- `core/` → esqueleto do serviço (ainda em evolução)
- `dashboard/` → dashboard estático inicial

## Rodar local (biblioteca + testes)
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -U pytest numpy scipy pydantic
pytest -q
```

## Rodar experimento (exemplo)
```bash
python experiments/autopoiesis_ab_test/run_experiment.py --config config.yaml --output results/
```

## Dashboard (estático)
```bash
cd dashboard
python -m http.server 5173
```

## Segurança

* Não commitar `.env`, chaves, tokens, bases/ledgers.
* Use `.env.example` como template.

## CI

O workflow roda:

* `black --check .`
* `pytest -q`
