# matverse-acoa/core

> **Versão:** 1.0  
> **Status:** Produção  
> **ORCID:** [0009-0008-2973-4047](https://orcid.org/0009-0008-2973-4047)  
> **Organização:** [matverse-acoa](https://github.com/matverse-acoa)

---

## Descrição

O repositório **`core`** constitui o núcleo científico-computacional do MatVerse, responsável por **materializar o fluxo Science → Evidence** segundo a Cláusula de Imutabilidade e a Lei de Admissibilidade Científica.

- **Função:** execução científica reprodutível, auditoria e verificação de métricas/invariantes.
- **Domínio:** coerência, risco de cauda, antifragilidade, auditabilidade e governança verificável.

---

## Cláusula Constitucional

> Este repositório é subordinado à Cláusula de Imutabilidade e à Lei de Admissibilidade Científica do MatVerse.  
> **Nada que comprometa o fluxo Science → Evidence será permitido, incorporado ou tolerado.**

Referências normativas nesta base:

- `docs/MATVERSE-OMEGA-GATE-v2.1-CANON.md`
- `docs/LEI_DE_ADMISSIBILIDADE_CIENTIFICA_MATVERSE_v1.0.md`

---

## Estrutura de Diretórios

```plaintext
core/
├── README.md
├── CONTRIBUTING.md
├── CODEOWNERS
├── src/acoa/
│   ├── core/
│   ├── metrics/
│   └── ...
├── tests/
├── docs/
├── experiments/
├── tools/
├── scripts/
└── deployments/
```

---

## Invariantes do Core

- **Ψ-Index:** coerência semântica observável.
- **CVaR:** controle de risco de cauda.
- **Ω-GATE:** operador de admissibilidade científica.
- **PoLE / PoSE:** evolução e evidência verificáveis.
- **Registro auditável:** artefatos assináveis e verificáveis por hash.

---

## Uso

```bash
# clonar repositório
git clone https://github.com/matverse-acoa/core
cd core

# instalar dependências
pip install -r requirements/base.txt
pip install -r requirements/dev.txt

# executar testes
pytest -q
```

---

## Contribuição

Leia o [CONTRIBUTING.md](CONTRIBUTING.md) para padrões de contribuição, critérios de revisão e requisitos de validação.

---

## Referências

- [MATVERSE-OMEGA-GATE v2.1 (canônico)](docs/MATVERSE-OMEGA-GATE-v2.1-CANON.md)
- [Lei de Admissibilidade Científica do MatVerse](docs/LEI_DE_ADMISSIBILIDADE_CIENTIFICA_MATVERSE_v1.0.md)

---

## Código de Conduta

Ao contribuir, você concorda com a impossibilidade de modificar retroativamente evidências ou violar invariantes formais já estabelecidos.

---

## Licença

[MIT License](LICENSE)
