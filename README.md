# 🧬 matverse-acoa/core

ACOA Core: métricas (Ψ, Ω, CVaR, CCR, α) + experimentos + base para governança binária (Ω-GATE).

[![Tests](https://github.com/matverse-acoa/core/actions/workflows/tests.yml/badge.svg)](https://github.com/matverse-acoa/core/actions/workflows/tests.yml)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0008--2973--4047-green)](https://orcid.org/0009-0008-2973-4047)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


ACOA Core é o **núcleo científico** do MatVerse.

Este repositório define, implementa e valida as **métricas invariantes**
que governam todo o sistema:

- Ψ — coerência semântica observável
- Ω — viabilidade sistêmica
- CVaR — risco de cauda
- CCR — consistência de decisão
- α — antifragilidade

Aqui vivem **leis mensuráveis**, não decisões e não execução.

---

## O que este repositório faz

- Implementa métricas formais em código auditável
- Executa experimentos científicos reprodutíveis
- Valida propriedades de coerência, risco e antifragilidade
- Produz artefatos verificáveis (JSON, hashes, relatórios)

---

## O que este repositório NÃO faz

- Não executa ações no mundo
- Não decide políticas
- Não escreve em ledgers de produção
- Não contém lógica de runtime
- Não depende de serviços externos

---

## Regime Arquitetural

**REGIME: LAW**

Este repositório define leis.
Leis não executam ações.
Leis não negociam com contexto.

Qualquer efeito colateral fora do processo científico é erro de arquitetura.

---

## Estrutura

- `src/acoa/` — biblioteca de métricas e invariantes
- `experiments/` — experimentos reprodutíveis
- `tools/` — utilitários (ex.: ancoragem, replay)
- `docs/` — especificações formais
- `tests/` — validação automatizada

---

## Garantias

- Determinismo
- Reprodutibilidade
- Auditabilidade externa
- Independência de autoridade humana

Este repositório é válido **mesmo isolado do resto do sistema**.
