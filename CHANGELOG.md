# Changelog

## [1.2.0] - 2026-11-25

### Segurança e privacidade (P0)

- `api/routes/progress.py` não aceita mais `user_id` do cliente. Progresso,
  favoritos, estatísticas, exportação e importação derivam a identidade de uma
  sessão autenticada (`api/auth.py`). `DEFAULT_USER` foi removido.
- Sessão **anônima** (`POST /api/session`): sem nome, e-mail ou CPF; o banco
  guarda só o hash SHA-256 do token, com validade deslizante de 180 dias.
- Escritas idempotentes: restrição única por (estudante, módulo), merges
  monotônicos e tratamento de `IntegrityError` para duplo clique.
- `tests/test_privacy.py` (30 testes) prova isolamento entre estudantes,
  rejeição de `user_id` no corpo (422) e ausência de dados pessoais.
- CORS deixou de ser lista fixa de localhost: agora é
  `APRENDE_CORS_ORIGINS`, e sem a variável não há CORS (o site é estático).

### Tutor LLM (P0)

- Modo generativo **desligado por padrão**: exige `LLM_ENABLED=1`.
- Timeout de 12 s, concorrência máxima, teto diário de caracteres, limite por
  IP, contexto truncado e *fallback* local em qualquer erro.
- Payload ao provedor não leva token, identidade nem dados pessoais
  (`tests/test_tutor_limits.py`).
- Motor local passou a recuperar o módulo por palavras do conteúdo e a oferecer
  **pistas** das atividades em vez da resposta pronta.

### Motor de conteúdo

- Contrato `StepData.content` ampliado de forma retrocompatível:
  `objectives`, `examples`, `vocabulary`, `references` e `activities`.
- Seis tipos de atividade implementados (múltipla escolha, verdadeiro/falso,
  lacuna, ordenação, associação e numérica), com validação no build em Python,
  no exportador e na CLI.
- **448 atividades** e objetivos em todos os 205 módulos, escritos em português
  brasileiro, sem infantilizar adultos.
- Gabaritos numéricos são avaliados no build (`numeric_checked`): conta errada
  quebra o build em vez de chegar ao estudante.

### Experiência do estudante

- Etapas agora mostram objetivos, atividades com feedback pedagógico e leitura
  em voz alta que inclui os enunciados.
- Acertar uma atividade marca a etapa de prática: fazer é a evidência.
- Nova página `/progresso`: tentativas, acertos, módulos com atividade,
  domínio por módulo, revisões pendentes, exportar, importar e reiniciar.
- Revisão espaçada (SM-2 adaptado) agendada na conclusão do módulo, com base no
  desempenho real — completar página não conta como domínio.
- Importação aditiva que ignora módulos inexistentes e nunca reduz progresso.

### PWA e offline

- Manifest, ícones (192/512/maskable) e service worker versionado.
- Atualização **nunca silenciosa**: a nova versão avisa e a pessoa escolhe
  recarregar; caches antigos são limpos na ativação.
- Faixa de estado para “sem conexão” e “versão nova disponível”.
- Service worker não cacheia `/api/` nem requisições com `Authorization`.

### Deploy

- `vite.config.ts`: `base` configurável por `VITE_BASE_PATH`; preview com hosts
  permitidos **explícitos e opcionais** (sem `allowedHosts: true` fixo); proxy
  `/api` no dev.
- `Base` do Vite muda assets e rotas juntos; o `404.html` é gerado com o mesmo
  base.
- Novo workflow `deploy-pages.yml` publica em `/aprende-brasil/` e verifica no
  CI que assets, `404.html`, `.nojekyll` e `open-data/` apontam para o subpath.
- `vercel.json`: reescrita que preserva `/api/`, `/assets/`, `/open-data/` e o
  manifest; CSP e cache por tipo de arquivo.
- `vite preview` deixa de devolver `index.html` para asset inexistente (404,
  como no FastAPI).
- `tools/aprende.mjs budget` entende builds em subpath.

### Testes

- Vitest: **104** (atividades, correção, SRS, armazenamento, renderizadores,
  tutor, a11y).
- pytest: **86** (API, privacidade, limites do tutor, dados, exportação,
  qualidade do conteúdo).
- Playwright: **21** testes em Chromium real (workflow `e2e.yml`), cobrindo
  busca, URL profunda, atividades, progresso, favoritos, teclado, contraste,
  exportação/importação, PWA e abertura offline.
- Nenhum número de Lighthouse foi medido neste ambiente: o Chromium não está
  disponível aqui, e o README diz isso explicitamente em vez de inventar
  pontuação.


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
- Path traversal no servidor de SPA (`/{full_path}` servia qualquer arquivo do
  disco); agora só entrega arquivos dentro de `dist/public`.

### Adicionado

- CLI `tools/aprende.mjs` (`stats`, `validate`, `budget`, `--help`).
- 54 testes novos: 52 Vitest (inclui axe-core) + 47 pytest.
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
