# Guia de Contribuição

Siga o processo abaixo para contribuir:

1. Faça um fork do repositório.
2. Crie uma branch de funcionalidade: `git checkout -b feature/nome-da-feature`.
3. Siga PEP8; use black e flake8.
4. Execute verificações obrigatórias (mypy).
5. Inclua testes (pytest) e garanta cobertura mínima local antes do PR.
6. PRs apenas com documentação não disparam CI; se você alterar workflows, o GitHub Actions sempre executa o CI para validar as mudanças.
7. Abra PR com descrição clara; duas aprovações mínimas.
8. Squash merge não é permitido.
