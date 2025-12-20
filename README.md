# ACOA Core

Implementação principal do **Adaptive Coherence-Oriented Audit (ACOA)**, com foco em
métricas de coerência operacional, auditoria adaptativa e monitoramento de risco
em ambientes dinâmicos. Este repositório reúne o núcleo de autopoiese (CCR), um
estimador CVaR streaming e um stub mínimo de API para integração inicial.

## Visão geral

O ACOA tem como objetivo fornecer mecanismos auditáveis e quantitativos para
avaliar a coerência e a viabilidade de sistemas complexos. Este núcleo inclui:

- **Autopoiesis/CCR**: mede fechamento operacional via *Causal Closure Rate*.
- **CVaR streaming**: estimador contínuo de risco extremo com suporte a CI via
  bootstrap.
- **API mínima (FastAPI)**: endpoint de saúde e auditoria para integração.
- **Experimentos A/B**: scripts de simulação para validação e análise.

## Estrutura do repositório

```
.
├── api/                       # Stub de API FastAPI
├── configs/                   # Configurações padrão
├── deployments/               # Assets de Docker
├── experiments/               # Scripts de experimentos A/B
├── requirements/              # Dependências base/dev
├── src/acoa/                  # Núcleo do ACOA
├── tests/                     # Smoke tests
└── RELEASE_NOTES/             # Notas de release
```

## Requisitos

- Python **>= 3.10**
- Recomendado: `venv` ou `pyenv`

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/dev.txt
```

## Uso rápido

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

## Exemplo de API (Python)

```python
from acoa import AutopoieticCore, SystemState
import numpy as np

core = AutopoieticCore()
state = SystemState(
    internal=np.array([1.0, 2.0]),
    external=np.array([0.5]),
    output=np.array([1.5, 2.5]),
    timestamp=1.0,
)
measurement = core.measure_ccr(state)
print(measurement.ccr)
```

## Testes e qualidade

```bash
pytest tests/ --maxfail=1 --disable-warnings -q
black --check .
flake8 src
mypy src
```

> Observação: alguns testes usam `numpy`. Em ambientes sem `numpy`, os testes
> correspondentes serão automaticamente ignorados.

## Roadmap (alto nível)

- Expandir validações e métricas de coerência.
- Endpoints de auditoria com integração completa ao núcleo ACOA.
- Persistência e observabilidade (Prometheus/Qdrant).

## Contribuição

Leia o [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes de contribuição.

## Licença

- **Código**: MIT (ver [LICENSE](LICENSE)).
- **Documentação/Preprints**: CC-BY-4.0.

## Citação

Se você usar este software, consulte [CITATION.cff](CITATION.cff).
