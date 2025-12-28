# UMJAM-OMEGA (Monorepo)
Sistema de governança pós-controle com ciclo CASSANDRA (R1–R4), Ω-GATE binário (EXECUTE/INTERDICT) e camada UMJAM-Ω (superblocks, ledger append-only, métrica Λ e serviços).

## Estrutura
- `core/` → núcleo Python (kernel + serviços + evidências)
- `dashboard/` → interface de monitoramento (static ou Vite)

## Requisitos
- Python 3.10+ (recomendado 3.11)
- (Opcional) Node 20+ se o dashboard for Vite/React

## Execução local (Core)
```bash
cd core
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Dependências (se existir requirements)
pip install -r requirements/base.txt

# Garantir libs-base
pip install -U numpy scipy pydantic

python main.py
```

## Dashboard (Static)

Se `dashboard/index.html` existir, abra no navegador ou sirva com um servidor simples:

```bash
cd dashboard
python -m http.server 5173
```

Abra: [http://localhost:5173](http://localhost:5173)

## Segurança (obrigatório)

* Nunca commitar `.env` nem chaves privadas.
* Use `.env.example` como template.
* Configure segredos somente em:

  * variáveis de ambiente locais, ou
  * Secrets/Variables do GitHub Actions, ou
  * Secrets/Variables do Hugging Face Space.

## CI

O workflow roda `pytest`. Se falhar, é sinal de repo incompleto (bom).
