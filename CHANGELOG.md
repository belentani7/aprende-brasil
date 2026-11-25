# Changelog

## [1.1.0] - 2026-11-25

### Restauração

- Recuperados os 156 arquivos do campus (frontend, API, dados, testes, deploy)
  a partir do snapshot versionado, devolvendo o projeto ao `main`.
- `main` volta a ter README, `package.json`, fontes, currículo e configuração
  de deploy.

### Conteúdo

- Alfabetização reescrita com 93 módulos curados: palavras comuns por letra,
  famílias silábicas reais, 24 temas de vocabulário, 12 tipos de frase e 10
  textos do dia a dia (receita, conta de luz, bula, contrato, cardápio…).
- Removidas sequências sem sentido geradas pelo banco aberto ("aabora, aac").
- Preços, medidas e exemplos revisados; estatísticas da página institucional
  agora derivam do currículo (205 módulos / 1.025 etapas / 4 trilhas).

### Performance

- Currículo dividido em catálogo (≈56 KB) e etapas (≈183 KB) carregadas sob
  demanda; JS inicial caiu de ≈146 KiB para ≈106 KiB gzip.
- Rotas `/modulo/:id`, `/sobre` e 404 em chunks próprios; motor do tutor
  carregado na primeira pergunta.
- Fontes auto-hospedadas (DM Sans, Syne, DM Mono), sem requisição ao Google
  Fonts e sem bloquear a primeira pintura.
- 501 dependências não utilizadas removidas (Radix, AWS SDK, Express, MySQL,
  Recharts, tRPC etc.); CSS caiu de ≈20,8 KiB para ≈10,3 KiB gzip.
- Orçamento de bundle automatizado em `tools/aprende.mjs`.

### Corrigido

- Divisão por zero nas barras das trilhas (`target_modules = 0`).
- Progresso e etapas marcadas agora são restaurados ao reabrir um módulo.
- Catálogo paginado de verdade: "carregar mais" e busca em todas as trilhas.
- Modal de módulo com `role="dialog"`, foco preso, `Esc` e devolução de foco.
- Viewport sem `maximum-scale` (zoom liberado); link "ir para o conteúdo".
- Página 404 traduzida e integrada ao produto.
- Atividade semanal real no painel, no lugar de números fixos.
- CI passou a executar typecheck, testes, build e orçamento; CodeQL corrigido.

### Adicionado

- CLI `tools/aprende.mjs` (`stats`, `validate`, `budget`, `--help`).
- 44 testes novos: 52 Vitest (inclui axe-core) + 42 pytest.
- `scripts/run-python.mjs` e `scripts/build-curriculum.mjs` para builds
  reproduzíveis com ou sem Python.
- Exportação determinística com modo `--check` para o CI.
- Exportador SQLAlchemy duplicado removido; `export_static_curriculum.py` é a
  única fonte de verdade dos JSON.

## [1.0.0] - 2025-10-15

### Added

- Initial repository setup with CI/CD (GitHub Actions)
- Standardized issue templates (bug_report.yml)
- Pull request template
- Security workflow (CodeQL scanning)
- Dependabot configuration
- Code of Conduct (Contributor Covenant 2.1)
- Security Policy (SECURITY.md)
- Contribution Guidelines (CONTRIBUTING.md)

### Security

- Enabled Dependabot alerts and security updates
- Added CodeQL workflow for automated security scanning
