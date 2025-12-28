# UMJAM-Ω Core

Este diretório concentra o kernel Python e os serviços associados ao ciclo
CASSANDRA (R1–R4), ao Ω-GATE binário (EXECUTE/INTERDICT) e às camadas UMJAM-Ω
(superblocks, ledger append-only, métrica Λ).

## Layout sugerido
- `main.py`: ponto de entrada do núcleo.
- `governance/`: regras, políticas e cadastros de atos.
- `interfaces/`: APIs, CLIs e adaptadores de integração.
- `infrastructure/`: persistência, filas, observabilidade.
- `umjam/`: lógica específica de superblocks/ledger.
- `requirements/`: arquivos de dependências (ex.: `base.txt`).

## Execução rápida
```bash
cd core
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/base.txt
python main.py
```
