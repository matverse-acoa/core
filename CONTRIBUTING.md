# Guia de Contribuição

## Princípios

Este repositório segue o regime **Science → Evidence**. Toda contribuição deve preservar determinismo, reprodutibilidade e auditabilidade.

## Fluxo de contribuição

1. Faça fork do repositório.
2. Crie uma branch: `git checkout -b feature/nome-da-feature`.
3. Siga padrões de estilo (PEP8) e mantenha mudanças pequenas e rastreáveis.
4. Adicione/atualize testes quando houver alteração funcional.
5. Execute checks locais antes do PR.
6. Abra PR com motivação, escopo e validação executada.

## Checks mínimos

```bash
pytest -q
```

Se sua mudança afetar tipagem, execute também:

```bash
mypy src
```

## Requisitos de PR

- Descrição clara do problema e da solução.
- Lista dos comandos executados para validação.
- Sem alteração retroativa de evidências/artifacts já publicados.
