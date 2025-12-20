# ACOA Core

[![Preprint-Authorea](https://img.shields.io/badge/Preprint-Authorea-blue)](https://www.authorea.com/doi/full/10.22541/au.XXXXXXX)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0008--2973--4047-green)](https://orcid.org/0009-0008-2973-4047)

Implementação de referência do **Adaptive Coherence-Oriented Audit (ACOA)**,
framework de governança pós-controle para organismos digitais autopoiéticos.
Baseado no **Preprint IV**: *Autopoiesis Without Control: Black-Box Digital
Organisms and Coherence-Based Governance via ACOA* (Arêas, 2024).

## ✅ Estado atual do repositório

**Status:** 🎉 **REPOSITÓRIO JÁ CRIADO E OPERACIONAL**

### Estrutura implementada

```
matverse-acoa/core/
├── ✅ .github/                # GitHub workflows
├── ✅ RELEASE_NOTES/          # Notas de versão
├── ✅ api/                    # FastAPI stub
├── ✅ configs/                # Configurações
├── ✅ deployments/docker/     # Docker setup
├── ✅ experiments/autopoiesis_ab_test/  # Protocolo experimental
├── ✅ requirements/           # Dependências (base/dev)
├── ✅ src/acoa/               # Core implementation
├── ✅ tests/                  # Smoke tests
├── ✅ README.md               # Documentação principal
├── ✅ CITATION.cff            # Citação acadêmica
├── ✅ CONTRIBUTING.md         # Guia de contribuição
├── ✅ LICENSE                 # MIT License
└── ✅ pyproject.toml          # Build config
```

### Funcionalidades implementadas

| Módulo | Status | Descrição |
|--------|--------|-----------|
| **AutopoieticCore** | ✅ | CCR measurement (causal closure) |
| **CVaR Estimator** | ✅ | Streaming tail risk estimator |
| **API Health** | ✅ | FastAPI health endpoint |
| **A/B Test** | ✅ | Experimental validation script |
| **Docker** | ✅ | Container setup |
| **Tests** | ✅ | Smoke tests (numpy-aware) |

## 🎯 Invariantes Fundamentais

Conforme **Preprint IV, Section 3.2**:

| Invariante | Símbolo | Definição | Threshold |
|-----------|---------|-----------|-----------|
| **Coherence** | Ψ | `1 - D_KL(P_t || P_ref)/D_max` | ≥ 0.85 |
| **Antifragility** | Ω | `E[V_post] / E[V_pre]` | > 1.0 |
| **Tail Risk** | CVaR | `E[L | L ≥ VaR_α]` | ≤ 0.30 |
| **Causal Closure** | CCR | `||∂ρ/∂x|| / ||∂ρ/∂u||` | > 1.0 |
| **Viability** | V | `w₁·uptime + w₂·(1-err) + w₃·rec` | ≥ 0.80 |

## 🧭 Gaps identificados

### Comparação: Preprint vs. GitHub

| Aspecto | Authorea (Publicado) | GitHub (Atual) | Gap |
|---------|---------------------|----------------|-----|
| **Coherence (Ψ)** | KL-divergence | Não implementado | ⚠️ CRÍTICO |
| **Viability (V)** | Weighted composite | Não implementado | ⚠️ CRÍTICO |
| **Antifragility (Ω)** | E[V_post]/E[V_pre] | Não implementado | ⚠️ CRÍTICO |
| **PoSE Contracts** | Especificado | Ausente | ⚠️ ALTO |
| **Documentation** | Completo | README básico | 🔶 MÉDIO |
| **Notebooks** | Esperado | Ausente | 🔶 MÉDIO |

## ⚙️ Requisitos

- Python **>= 3.10**
- Recomendado: `venv` ou `pyenv`

## 📦 Instalação

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/dev.txt
```

## 🚀 Uso rápido

### API (stub)

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

```bash
curl http://localhost:8000/health
```

### Experimento A/B (autopoiesis)

```bash
python experiments/autopoiesis_ab_test/run_experiment.py \
  --config experiments/autopoiesis_ab_test/config.yaml \
  --output experiments/autopoiesis_ab_test/results
```

## 🧪 Testes e qualidade

```bash
pytest tests/ --maxfail=1 --disable-warnings -q
black --check .
flake8 src
mypy src
```

> Observação: alguns testes usam `numpy`. Em ambientes sem `numpy`, os testes
> correspondentes serão automaticamente ignorados.

## 🗺️ Roadmap (alto nível)

- Implementar **Coherence (Ψ)** via KL divergence.
- Implementar **Viability (V)** com composição ponderada.
- Implementar **Antifragility (Ω)** com `E[V_post]/E[V_pre]`.
- Sincronizar documentação com o preprint (Authorea).

## 🤝 Contribuição

Leia o [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes de contribuição.

## 📜 Licença

- **Código**: MIT (ver [LICENSE](LICENSE)).
- **Documentação/Preprints**: CC-BY-4.0.

## 📚 Citação

Se você usar este software, consulte [CITATION.cff](CITATION.cff).
